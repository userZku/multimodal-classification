from __future__ import annotations

import json
import logging
import pickle
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

try:
    from xgboost.core import XGBoostError
except ImportError:

    class XGBoostError(Exception):
        pass


from src.config import (
    ABSTENTION_THRESHOLD,
    BEST_MODEL_METADATA_PATH,
    BEST_MODEL_PATH,
    MLFLOW_DIR,
    PRODUCTION_SCENARIO,
    PROJECT_ROOT,
)
from src.features.preprocessing import build_model_frame
from src.api.feedback_store import FeedbackStore
from scripts.retrain_feedback import run_retrain_cycle
from src.api.schemas import (
    FeedbackCountResponse,
    FeedbackRequest,
    FeedbackResponse,
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

FEEDBACK_STORE = FeedbackStore()

UI_DIR = PROJECT_ROOT / "app" / "ui"

if UI_DIR.exists():
    app.mount("/ui", StaticFiles(directory=UI_DIR), name="ui")


def load_artifacts() -> tuple[object | None, dict]:
    metadata = (
        json.loads(BEST_MODEL_METADATA_PATH.read_text(encoding="utf-8"))
        if BEST_MODEL_METADATA_PATH.exists()
        else {}
    )
    pipeline = None
    if BEST_MODEL_PATH.exists() and metadata.get("scenario") == PRODUCTION_SCENARIO:
        try:
            pipeline = joblib.load(BEST_MODEL_PATH)
        except (
            EOFError,
            pickle.UnpicklingError,
            ImportError,
            AttributeError,
            OSError,
            XGBoostError,
        ) as exc:
            # API must stay up even if local model artifact cannot be deserialized.
            logging.getLogger("api.predict").warning(
                "Failed to load pipeline artifact %s: %s", BEST_MODEL_PATH, exc
            )
            pipeline = None
    elif BEST_MODEL_PATH.exists():
        logging.getLogger("api.predict").warning(
            "Model artifact scenario is not %s; retrain before serving predictions.",
            PRODUCTION_SCENARIO,
        )
    return pipeline, metadata


PIPELINE, METADATA = load_artifacts()


def model_version() -> str:
    trained_at = METADATA.get("trained_at")
    if trained_at:
        return f"xgb-s2-{trained_at}"
    return "unavailable"


PREDICT_COUNTER = Counter("api_predict_total", "Number of predict requests", ["status"])
PREDICT_LATENCY = Histogram(
    "api_predict_latency_seconds", "Latency of predict endpoint"
)
TRAIN_COUNTER = Counter("api_train_total", "Number of train requests", ["status"])
TRAIN_LATENCY = Histogram("api_train_latency_seconds", "Latency of train endpoint")

JSONL_PREDICT_EVENTS = Gauge(
    "api_jsonl_predict_events_total", "Number of prediction events found in JSONL logs"
)
JSONL_TRAIN_EVENTS = Gauge(
    "api_jsonl_train_events_total", "Number of train events found in JSONL logs"
)
JSONL_TRAIN_ERRORS = Gauge(
    "api_jsonl_train_error_events_total",
    "Number of failed train events found in JSONL logs",
)
MLFLOW_EXPERIMENTS = Gauge(
    "api_mlflow_experiments_total", "Number of MLflow experiments found in local store"
)
MLFLOW_RUNS = Gauge(
    "api_mlflow_runs_total", "Number of MLflow runs found in local store"
)

PREDICTION_CLASS_COUNTER = Counter(
    "api_prediction_class_total",
    "Number of predictions by predicted class",
    ["predicted_class"],
)
PREDICTION_CONFIDENCE = Histogram(
    "api_prediction_confidence",
    "Confidence (max probability) of the predicted class",
    buckets=(0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.70, 0.80, 0.90, 0.95, 1.0),
)
PREDICTION_PROBA_SUM = Counter(
    "api_prediction_proba",
    "Cumulative predicted probability per class (divide by predict count for the mean)",
    ["class_label"],
)
MODEL_QUALITY = Gauge(
    "api_model_metric",
    "Offline evaluation metrics of the currently served model",
    ["metric"],
)

# Pre-create label combinations so panels show 0 instead of "No data".
for _status in ("ok", "a_revoir", "error", "model_not_ready"):
    PREDICT_COUNTER.labels(status=_status)
for _status in ("ok", "error"):
    TRAIN_COUNTER.labels(status=_status)
for _class in ("0", "1", "2"):
    PREDICTION_CLASS_COUNTER.labels(predicted_class=_class)
    PREDICTION_PROBA_SUM.labels(class_label=_class)

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


def _refresh_model_quality_metrics() -> None:
    for name, value in (METADATA.get("metrics") or {}).items():
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            MODEL_QUALITY.labels(metric=name).set(float(value))


def reload_artifacts() -> None:
    global PIPELINE, METADATA
    PIPELINE, METADATA = load_artifacts()
    _refresh_model_quality_metrics()


def _count_file_lines(file_path: Path) -> int:
    if not file_path.exists():
        return 0
    with file_path.open("r", encoding="utf-8") as handle:
        return sum(1 for _ in handle)


def _count_train_error_events(file_path: Path) -> int:
    if not file_path.exists():
        return 0

    errors = 0
    with file_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("status") == "error":
                errors += 1
    return errors


def _scan_mlflow_store(mlflow_root: Path) -> tuple[int, int]:
    if not mlflow_root.exists():
        return 0, 0

    experiment_dirs = [
        path
        for path in mlflow_root.iterdir()
        if path.is_dir() and path.name not in {".trash", "models"}
    ]

    experiments = 0
    runs = 0
    for exp_dir in experiment_dirs:
        if not (exp_dir / "meta.yaml").exists():
            continue
        experiments += 1
        runs += sum(
            1
            for candidate in exp_dir.iterdir()
            if candidate.is_dir() and (candidate / "meta.yaml").exists()
        )

    return experiments, runs


def _refresh_derived_metrics() -> None:
    JSONL_PREDICT_EVENTS.set(float(_count_file_lines(PREDICT_LOG_PATH)))
    JSONL_TRAIN_EVENTS.set(float(_count_file_lines(TRAIN_LOG_PATH)))
    JSONL_TRAIN_ERRORS.set(float(_count_train_error_events(TRAIN_LOG_PATH)))

    exp_count, run_count = _scan_mlflow_store(MLFLOW_DIR)
    MLFLOW_EXPERIMENTS.set(float(exp_count))
    MLFLOW_RUNS.set(float(run_count))

    _refresh_model_quality_metrics()


def _read_jsonl_tail(file_path: Path, limit: int) -> list[dict]:
    if limit <= 0 or not file_path.exists():
        return []

    events: list[dict] = []
    with file_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return events[-limit:]


def _find_logged_prediction(request_id: str) -> dict | None:
    """Look up a previously logged /predict event by its request_id."""
    if not PREDICT_LOG_PATH.exists():
        return None
    with PREDICT_LOG_PATH.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("request_id") == request_id:
                return event
    return None


@app.get("/", include_in_schema=False)
def ui_home() -> FileResponse:
    return FileResponse(UI_DIR / "index.html")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    loaded = PIPELINE is not None
    return HealthResponse(
        status="ok",
        model_loaded=loaded,
        model_version=model_version() if loaded else "unavailable",
        run_id=METADATA.get("mlflow", {}).get("run_id"),
    )


@app.get("/metrics")
def metrics() -> Response:
    _refresh_derived_metrics()
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/history")
def history(limit: int = Query(default=20, ge=1, le=200)) -> dict:
    items = _read_jsonl_tail(PREDICT_LOG_PATH, limit=limit)
    return {
        "count": len(items),
        "items": items,
    }


@app.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest) -> PredictResponse:
    if PIPELINE is None:
        PREDICT_COUNTER.labels(status="model_not_ready").inc()
        raise HTTPException(
            status_code=503, detail="Model artifact not found. Train model first."
        )

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
            PREDICTION_CLASS_COUNTER.labels(predicted_class=str(prediction)).inc()
            PREDICTION_CONFIDENCE.observe(confidence)
            for class_index, class_proba in enumerate(proba):
                PREDICTION_PROBA_SUM.labels(class_label=str(class_index)).inc(
                    float(class_proba)
                )
        except (
            ValueError,
            KeyError,
            TypeError,
            IndexError,
            AttributeError,
            RuntimeError,
        ) as exc:
            PREDICT_COUNTER.labels(status="error").inc()
            logger.exception("Prediction failed for request %s", request_id)
            raise HTTPException(
                status_code=500, detail=f"Prediction failed: {exc}"
            ) from exc

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
def retrain(payload: TrainRequest) -> TrainResponse:
    with TRAIN_LATENCY.time():
        try:
            result = run_retrain_cycle(
                min_feedback=0,
                dataset_path=payload.dataset_path,
                trigger=payload.trigger,
            )
            if result["status"] == "promoted":
                reload_artifacts()
            TRAIN_COUNTER.labels(status="ok").inc()
        except (FileNotFoundError, OSError, ValueError, RuntimeError, TypeError) as exc:
            TRAIN_COUNTER.labels(status="error").inc()
            train_logger.info(
                json.dumps(
                    {
                        "timestamp_utc": datetime.now(tz=timezone.utc).isoformat(),
                        "status": "error",
                        "dataset_path": payload.dataset_path,
                        "trigger": payload.trigger,
                        "error": str(exc),
                    },
                    ensure_ascii=False,
                )
            )
            logging.getLogger("api.train").exception("Training failed")
            raise HTTPException(
                status_code=500, detail=f"Training failed: {exc}"
            ) from exc

    train_logger.info(
        json.dumps(
            {
                "timestamp_utc": datetime.now(tz=timezone.utc).isoformat(),
                "event_id": result["event_id"],
                "status": "ok",
                "outcome": result["status"],
                "dataset_path": payload.dataset_path,
                "trigger": payload.trigger,
                "model_version": model_version(),
                "metrics": result.get("candidate_metrics", {}),
                "reason": result.get("reason"),
            },
            ensure_ascii=False,
        )
    )

    return TrainResponse(
        status=result["status"],
        event_id=result["event_id"],
        model_version=model_version(),
        run_id=result.get("mlflow_run_id"),
        metrics=result.get("candidate_metrics", {}),
        reason=result.get("reason"),
    )


@app.post("/feedback", response_model=FeedbackResponse, status_code=201)
def post_feedback(payload: FeedbackRequest) -> FeedbackResponse:
    logged_event = _find_logged_prediction(payload.request_id)
    if logged_event is None:
        raise HTTPException(
            status_code=404,
            detail=f"request_id inconnu : {payload.request_id} n'a jamais été prédit",
        )

    status, http_code = FEEDBACK_STORE.insert_or_conflict(
        payload.request_id, payload.true_label, payload.comments
    )

    if http_code == 409:
        raise HTTPException(
            status_code=409,
            detail=f"Feedback conflictuel : {payload.request_id} existe avec un label différent",
        )

    return FeedbackResponse(
        status="stored",
        message=f"Feedback {status} pour {payload.request_id}",
        feedback_id=payload.request_id,
    )


@app.get("/feedback/count", response_model=FeedbackCountResponse)
def get_feedback_count() -> FeedbackCountResponse:
    return FeedbackCountResponse(**FEEDBACK_STORE.get_count())


@app.get("/feedback/health")
def feedback_health() -> dict:
    counts = FEEDBACK_STORE.get_count()
    return {
        "status": "ok",
        "total_feedbacks": counts["total"],
        "unconsumed_feedbacks": counts["new"],
    }
