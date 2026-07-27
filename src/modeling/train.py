from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

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
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    RANDOM_STATE,
    TARGET_COL,
    TEXT_FEATURE,
)
from src.features.preprocessing import build_model_frame, build_preprocessor, resolve_feature_spec


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

    # Parametres XGBoost alignes avec la variante S1 du notebook.
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

    return Pipeline([
        ("prep", preprocessor),
        ("clf", classifier),
    ])


def train_and_save_model(csv_path: str | None = None) -> dict:
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

    # Scenario S1: toutes les features modele (numeriques + categorielles + texte)
    num_feats = [c for c in NUMERIC_FEATURES if c in X_train.columns]
    cat_feats = [c for c in CATEGORICAL_FEATURES if c in X_train.columns and c != TEXT_FEATURE]
    unknown_features = sorted(set(X_train.columns) - set(num_feats) - set(cat_feats) - {TEXT_FEATURE})
    if unknown_features:
        raise ValueError(f"Features non mappees pour S1_multimodal_complet: {unknown_features}")

    pipeline = build_training_pipeline(X_train.columns.tolist())
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    cm = confusion_matrix(y_test, y_pred, labels=[0, 1, 2]).tolist()
    critical_errors = int(((y_test == CRITICAL_CLASS) & (y_pred == 0)).sum())

    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "f1_macro": float(f1_score(y_test, y_pred, average="macro")),
        "recall_class_2": float(
            recall_score(y_test, y_pred, labels=[CRITICAL_CLASS], average="macro", zero_division=0)
        ),
        "critical_2_to_0": critical_errors,
        "test_size": int(len(y_test)),
        "confusion_matrix": cm,
    }

    BEST_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, BEST_MODEL_PATH)

    metadata = {
        "model_name": "xgboost",
        "scenario": "S1_multimodal_complet",
        "trained_at": datetime.now(tz=timezone.utc).isoformat(),
        "features": X_train.columns.tolist(),
        "metrics": metrics,
    }
    BEST_MODEL_METADATA_PATH.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description="Train and serialize model artifacts from the project dataset")
    parser.add_argument("--csv-path", dest="csv_path", default=None, help="Optional path to a custom training CSV")
    args = parser.parse_args()

    metadata = train_and_save_model(csv_path=args.csv_path)
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
