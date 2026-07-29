from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from uuid import uuid4

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from src.config import ABSTENTION_THRESHOLD, BEST_MODEL_METADATA_PATH, BEST_MODEL_PATH, PROJECT_ROOT
from src.features.preprocessing import build_model_frame
from src.modeling.train import train_and_save_model
from src.api.schemas import (
    HealthResponse,
    PredictRequest,
    PredictResponse,
    TrainRequest,
    TrainResponse,
)

app = FastAPI(
    title="Multimodal Classification API",
    version="1.0.0",
    description="Inference API for return-to-employment delay classification.",
)


def load_artifacts() -> tuple[object | None, dict]:
    pipeline = None
    if BEST_MODEL_PATH.exists():
        try:
            pipeline = joblib.load(BEST_MODEL_PATH)
        except Exception:
            # API must stay up even if local model artifact cannot be deserialized.
            pipeline = None
    metadata = (
        json.loads(BEST_MODEL_METADATA_PATH.read_text(encoding="utf-8"))
        if BEST_MODEL_METADATA_PATH.exists()
        else {}
    )
    return pipeline, metadata


PIPELINE, METADATA = load_artifacts()


def model_version() -> str:
    trained_at = METADATA.get("trained_at")
    if trained_at:
        return f"xgb-s1-{trained_at}"
    return "unavailable"

PREDICT_COUNTER = Counter("api_predict_total", "Number of predict requests", ["status"])
PREDICT_LATENCY = Histogram("api_predict_latency_seconds", "Latency of predict endpoint")
TRAIN_COUNTER = Counter("api_train_total", "Number of train requests", ["status"])
TRAIN_LATENCY = Histogram("api_train_latency_seconds", "Latency of train endpoint")

LOG_DIR = PROJECT_ROOT / "logs" / "inference"
LOG_DIR.mkdir(parents=True, exist_ok=True)
PREDICT_LOG_PATH = LOG_DIR / "api_predict_requests.jsonl"
TRAIN_LOG_PATH = LOG_DIR / "api_train_events.jsonl"

logger = logging.getLogger("api.predict")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(PREDICT_LOG_PATH, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)

train_logger = logging.getLogger("api.train")
if not train_logger.handlers:
    train_logger.setLevel(logging.INFO)
    train_handler = logging.FileHandler(TRAIN_LOG_PATH, encoding="utf-8")
    train_handler.setFormatter(logging.Formatter("%(message)s"))
    train_logger.addHandler(train_handler)


def reload_artifacts() -> None:
    global PIPELINE, METADATA
    PIPELINE, METADATA = load_artifacts()


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        model_loaded=PIPELINE is not None,
        model_version=model_version(),
    )


@app.get("/metrics")
def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest) -> PredictResponse:
    if PIPELINE is None:
        PREDICT_COUNTER.labels(status="model_not_ready").inc()
        raise HTTPException(status_code=503, detail="Model artifact not found. Train model first.")

    request_id = f"req_{datetime.now(tz=timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:6]}"
    payload_dict = payload.model_dump()

    with PREDICT_LATENCY.time():
        try:
            frame = pd.DataFrame([payload_dict])
            model_frame = build_model_frame(frame)

            proba = PIPELINE.predict_proba(model_frame)[0]
            prediction = int(proba.argmax())
            confidence = float(proba.max())
            status = "a_revoir" if confidence < ABSTENTION_THRESHOLD else "ok"

            PREDICT_COUNTER.labels(status=status).inc()
        except Exception as exc:  # defensive path for runtime errors
            PREDICT_COUNTER.labels(status="error").inc()
            raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}") from exc

    log_event = {
        "timestamp_utc": datetime.now(tz=timezone.utc).isoformat(),
        "request_id": request_id,
        "input": payload_dict,
        "output": {
            "prediction": prediction,
            "confidence": confidence,
            "status": status,
            "model_version": model_version(),
        },
    }
    logger.info(json.dumps(log_event, ensure_ascii=False))

    return PredictResponse(
        prediction=prediction,
        confidence=confidence,
        status=status,
        model_version=model_version(),
        request_id=request_id,
    )


@app.post("/retrain", response_model=TrainResponse)
@app.post("/train", response_model=TrainResponse)
def retrain(payload: TrainRequest) -> TrainResponse:
    event_id = f"train_{datetime.now(tz=timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:6]}"

    with TRAIN_LATENCY.time():
        try:
            metadata = train_and_save_model(
                csv_path=payload.dataset_path,
                mlflow_tracking_uri=payload.mlflow_tracking_uri,
                mlflow_experiment=payload.mlflow_experiment,
            )
            reload_artifacts()
            TRAIN_COUNTER.labels(status="ok").inc()
        except Exception as exc:
            TRAIN_COUNTER.labels(status="error").inc()
            train_logger.info(
                json.dumps(
                    {
                        "timestamp_utc": datetime.now(tz=timezone.utc).isoformat(),
                        "event_id": event_id,
                        "status": "error",
                        "dataset_path": payload.dataset_path,
                        "trigger": payload.trigger,
                        "error": str(exc),
                    },
                    ensure_ascii=False,
                )
            )
            raise HTTPException(status_code=500, detail=f"Training failed: {exc}") from exc

    train_logger.info(
        json.dumps(
            {
                "timestamp_utc": datetime.now(tz=timezone.utc).isoformat(),
                "event_id": event_id,
                "status": "ok",
                "dataset_path": payload.dataset_path,
                "trigger": payload.trigger,
                "model_version": model_version(),
                "metrics": metadata.get("metrics", {}),
            },
            ensure_ascii=False,
        )
    )

    return TrainResponse(
        status="ok",
        event_id=event_id,
        model_version=model_version(),
        metrics=metadata.get("metrics", {}),
    )
