from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    FunctionTransformer,
    OneHotEncoder,
    OrdinalEncoder,
    StandardScaler,
)

from src.config import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    ORDINAL_CATEGORIES,
    ORDINAL_FEATURES,
    TARGET_COL,
    TEXT_FEATURE,
)


@dataclass(frozen=True)
class FeatureSpec:
    numeric: list[str]
    ordinal: list[str]
    categorical: list[str]
    text: str


def _to_text_series(s: pd.DataFrame | pd.Series) -> pd.Series:
    """Convert the incoming text column slice to a clean 1D text series."""
    squeezed = s.squeeze()
    if isinstance(squeezed, pd.Series):
        return squeezed.fillna("").astype(str)
    # Defensive path for single-value inference inputs.
    if pd.isna(squeezed):
        return pd.Series([""])
    return pd.Series([str(squeezed)])


def infer_departement_from_insee(code_insee_commune: pd.Series) -> pd.Series:
    insee_clean = (
        code_insee_commune.astype("string")
        .fillna("")
        .str.strip()
        .str.upper()
        .str.replace(r"[^0-9A-Z]", "", regex=True)
        .str.zfill(5)
    )
    return insee_clean.str[:2].replace({"": pd.NA})


def apply_feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "departement_insee" not in out.columns and "code_insee_commune" in out.columns:
        out["departement_insee"] = infer_departement_from_insee(
            out["code_insee_commune"]
        )
    return out


def resolve_feature_spec(columns: Iterable[str]) -> FeatureSpec:
    cols = set(columns)
    numeric = [c for c in NUMERIC_FEATURES if c in cols]
    ordinal = [c for c in ORDINAL_FEATURES if c in cols]
    categorical = [c for c in CATEGORICAL_FEATURES if c in cols and c != TEXT_FEATURE]
    return FeatureSpec(
        numeric=numeric,
        ordinal=ordinal,
        categorical=categorical,
        text=TEXT_FEATURE,
    )


def build_model_frame(df: pd.DataFrame) -> pd.DataFrame:
    work = apply_feature_engineering(df)
    drop_cols = [
        c
        for c in ["usager_id", "code_insee_commune", "nationalite_hors_ue"]
        if c in work.columns
    ]
    return work.drop(columns=drop_cols, errors="ignore")


def split_xy(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    if TARGET_COL not in df.columns:
        raise ValueError(f"Missing target column: {TARGET_COL}")
    X = build_model_frame(df.drop(columns=[TARGET_COL]))
    y = df[TARGET_COL].copy()
    return X, y


def build_preprocessor(spec: FeatureSpec, use_text: bool = True) -> ColumnTransformer:
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    ordinal_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "encoder",
                OrdinalEncoder(
                    categories=ORDINAL_CATEGORIES,
                    handle_unknown="use_encoded_value",
                    unknown_value=-1,
                ),
            ),
        ]
    )

    text_pipeline = Pipeline(
        steps=[
            (
                "to_text",
                FunctionTransformer(_to_text_series, validate=False),
            ),
            ("tfidf", TfidfVectorizer(max_features=500, ngram_range=(1, 2))),
        ]
    )

    transformers: list[tuple[str, Pipeline, list[str]]] = [
        ("num", numeric_pipeline, spec.numeric),
        ("ord", ordinal_pipeline, spec.ordinal),
        ("cat", categorical_pipeline, spec.categorical),
    ]
    if use_text:
        transformers.append(("txt", text_pipeline, [spec.text]))

    return ColumnTransformer(transformers=transformers, remainder="drop")
