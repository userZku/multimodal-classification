from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DATA_RAW_DIR = DATA_DIR / "raw"
MODELS_DIR = PROJECT_ROOT / "models"
BEST_MODEL_DIR = MODELS_DIR / "best_model"
BEST_MODEL_PATH = BEST_MODEL_DIR / "model.joblib"
BEST_MODEL_METADATA_PATH = BEST_MODEL_DIR / "metadata.json"
MLFLOW_DIR = PROJECT_ROOT / "mlruns"
MLFLOW_EXPERIMENT = "multimodal-classification"

RANDOM_STATE = 42
TARGET_COL = "classe_retour_emploi"
TEXT_FEATURE = "synthese_entretien"

NUMERIC_FEATURES = ["age", "anciennete_poste_ans"]
CATEGORICAL_FEATURES = [
    "niveau_diplome",
    "code_rome_vise",
    "est_allocataire",
    "departement_insee",
]

PRODUCTION_SCENARIO = "S2_sans_variable_sensible"
CRITICAL_CLASS = 2
ABSTENTION_THRESHOLD = 0.55
