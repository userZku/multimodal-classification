from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from src.config import (
    BEST_MODEL_DIR,
    BEST_MODEL_METADATA_PATH,
    BEST_MODEL_PATH,
    CRITICAL_CLASS,
    DATA_DIR,
    DATA_RAW_DIR,
    MLFLOW_DIR,
    MLFLOW_EXPERIMENT,
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    ORDINAL_FEATURES,
    PRODUCTION_SCENARIO,
    RANDOM_STATE,
    TARGET_COL,
    TEXT_FEATURE,
)
from src.features.preprocessing import (
    build_model_frame,
    build_preprocessor,
    resolve_feature_spec,
)


def load_training_data(csv_path: str | None = None) -> pd.DataFrame:
    if csv_path:
        return pd.read_csv(csv_path)

    candidates = sorted(DATA_RAW_DIR.glob("*.csv"))
    if not candidates:
        candidates = sorted(DATA_DIR.glob("*.csv"))
    if not candidates:
        raise FileNotFoundError("No CSV dataset found in data/raw or data")
    return pd.read_csv(candidates[0])


def build_training_pipeline(feature_columns: list[str]) -> Pipeline:
    from xgboost import XGBClassifier

    spec = resolve_feature_spec(feature_columns)
    preprocessor = build_preprocessor(spec, use_text=True)

    # Parametres XGBoost alignes avec la variante S2 du notebook.
    classifier = XGBClassifier(
        n_estimators=450,
        max_depth=5,
        learning_rate=0.03,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="multi:softprob",
        num_class=3,
        eval_metric="mlogloss",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    return Pipeline(
        [
            ("prep", preprocessor),
            ("clf", classifier),
        ]
    )


def _setup_mlflow(tracking_uri: str | None = None, experiment_name: str | None = None):
    import mlflow

    effective_tracking_uri = tracking_uri or str(MLFLOW_DIR.resolve())
    if "://" not in effective_tracking_uri:
        effective_tracking_uri = Path(effective_tracking_uri).resolve().as_uri()

    # MLflow 2.16+ blocks filesystem store by default unless this flag is set.
    if effective_tracking_uri.startswith("file://"):
        os.environ.setdefault("MLFLOW_ALLOW_FILE_STORE", "true")

    mlflow.set_tracking_uri(effective_tracking_uri)
    mlflow.set_experiment(experiment_name or MLFLOW_EXPERIMENT)
    return mlflow, effective_tracking_uri


def _log_mlflow_run(
    *,
    mlflow,
    pipeline: Pipeline,
    metrics: dict,
    feature_columns: list[str],
    dataset_ref: str,
    model_path: Path,
) -> tuple[str, str]:
    clf = pipeline.named_steps["clf"]
    params = {
        "scenario": PRODUCTION_SCENARIO,
        "model_name": "xgboost",
        "random_state": RANDOM_STATE,
        "dataset_ref": dataset_ref,
        "n_features": len(feature_columns),
        "n_estimators": int(getattr(clf, "n_estimators", 0)),
        "max_depth": int(getattr(clf, "max_depth", 0)),
        "learning_rate": float(getattr(clf, "learning_rate", 0.0)),
        "subsample": float(getattr(clf, "subsample", 0.0)),
        "colsample_bytree": float(getattr(clf, "colsample_bytree", 0.0)),
    }
    numeric_metrics = {k: v for k, v in metrics.items() if isinstance(v, (int, float))}

    with mlflow.start_run(run_name="xgboost-s2-train") as run:
        mlflow.log_params(params)
        mlflow.log_metrics(numeric_metrics)
        mlflow.log_dict({"features": feature_columns}, "features.json")
        mlflow.log_dict(metrics, "metrics.json")
        mlflow.log_artifact(str(model_path), artifact_path="model_artifacts")
        return run.info.run_id, run.info.experiment_id


def train_and_save_model(
    csv_path: str | None = None,
    *,
    mlflow_tracking_uri: str | None = None,
    mlflow_experiment: str | None = None,
) -> dict:
    mlflow, effective_tracking_uri = _setup_mlflow(
        tracking_uri=mlflow_tracking_uri,
        experiment_name=mlflow_experiment,
    )

    df = load_training_data(csv_path=csv_path)
    if TARGET_COL not in df.columns:
        raise ValueError(f"Target column missing: {TARGET_COL}")

    y = df[TARGET_COL].copy()
    X_raw = df.drop(columns=[TARGET_COL]).copy()
    X_model = build_model_frame(X_raw)

    X_train, X_test, y_train, y_test = train_test_split(
        X_model,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y,
        shuffle=True,
    )

    # Scenario S2: variables multimodales sans nationalite_hors_ue.
    num_feats = [c for c in NUMERIC_FEATURES if c in X_train.columns]
    ordinal_feats = [c for c in ORDINAL_FEATURES if c in X_train.columns]
    cat_feats = [
        c for c in CATEGORICAL_FEATURES if c in X_train.columns and c != TEXT_FEATURE
    ]
    unknown_features = sorted(
        set(X_train.columns)
        - set(num_feats)
        - set(ordinal_feats)
        - set(cat_feats)
        - {TEXT_FEATURE}
    )
    if unknown_features:
        raise ValueError(
            f"Features non mappees pour {PRODUCTION_SCENARIO}: {unknown_features}"
        )

    pipeline = build_training_pipeline(X_train.columns.tolist())
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    cm = confusion_matrix(y_test, y_pred, labels=[0, 1, 2]).tolist()
    critical_errors = int(((y_test == CRITICAL_CLASS) & (y_pred == 0)).sum())

    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "f1_macro": float(f1_score(y_test, y_pred, average="macro")),
        "recall_class_2": float(
            recall_score(
                y_test,
                y_pred,
                labels=[CRITICAL_CLASS],
                average="macro",
                zero_division=0,
            )
        ),
        "critical_2_to_0": critical_errors,
        "test_size": int(len(y_test)),
        "confusion_matrix": cm,
    }

    BEST_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, BEST_MODEL_PATH)

    run_id, experiment_id = _log_mlflow_run(
        mlflow=mlflow,
        pipeline=pipeline,
        metrics=metrics,
        feature_columns=X_train.columns.tolist(),
        dataset_ref=csv_path or "auto:data/raw/*.csv|data/*.csv",
        model_path=BEST_MODEL_PATH,
    )

    metadata = {
        "model_name": "xgboost",
        "scenario": PRODUCTION_SCENARIO,
        "trained_at": datetime.now(tz=timezone.utc).isoformat(),
        "features": X_train.columns.tolist(),
        "metrics": metrics,
        "mlflow": {
            "tracking_uri": effective_tracking_uri,
            "experiment_name": mlflow_experiment or MLFLOW_EXPERIMENT,
            "experiment_id": experiment_id,
            "run_id": run_id,
        },
    }
    BEST_MODEL_METADATA_PATH.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Train and serialize model artifacts from the project dataset"
    )
    parser.add_argument(
        "--csv-path",
        dest="csv_path",
        default=None,
        help="Optional path to a custom training CSV",
    )
    parser.add_argument(
        "--mlflow-tracking-uri",
        dest="mlflow_tracking_uri",
        default=None,
        help="MLflow tracking URI (default: local mlruns folder)",
    )
    parser.add_argument(
        "--mlflow-experiment",
        dest="mlflow_experiment",
        default=None,
        help="MLflow experiment name (default from config)",
    )
    args = parser.parse_args()

    metadata = train_and_save_model(
        csv_path=args.csv_path,
        mlflow_tracking_uri=args.mlflow_tracking_uri,
        mlflow_experiment=args.mlflow_experiment,
    )
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
