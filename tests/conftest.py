from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(autouse=True, scope="session")
def _ensure_model_pipeline_loaded():
    """Garantit qu'un modèle est chargé pour que /predict fonctionne en CI.

    `models/` est gitignoré (artefacts locaux) : en CI, aucun modèle réel
    n'est présent tant qu'un entraînement n'a pas été lancé. Les tests qui
    ont besoin d'un vrai `PIPELINE` (ex. `/predict` via `_make_prediction()`
    dans les tests de la boucle de feedback) fonctionnent quand même grâce à
    ce pipeline factice, sans dépendre d'un artefact entraîné au préalable.
    """
    import src.api.main as api_main

    if api_main.PIPELINE is not None:
        return

    class _FakePipeline:
        def predict_proba(self, _frame):
            return np.array([[0.10, 0.20, 0.70]])

    api_main.PIPELINE = _FakePipeline()
    api_main.METADATA = {"trained_at": "test-fixture", "metrics": {}}
