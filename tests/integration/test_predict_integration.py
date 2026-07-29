from __future__ import annotations

import numpy as np
from fastapi.testclient import TestClient

from src.api.main import app
import src.api.main as api_main

client = TestClient(app)


class FakePipeline:
    def __init__(self, proba: list[list[float]]) -> None:
        self._proba = np.array(proba, dtype=float)

    def predict_proba(self, _model_frame):  # noqa: ANN001
        return self._proba


def _valid_payload() -> dict:
    return {
        "usager_id": "U_TEST_001",
        "age": 35,
        "niveau_diplome": "Bac",
        "anciennete_poste_ans": 4.0,
        "code_rome_vise": "M1602",
        "est_allocataire": 1,
        "nationalite_hors_ue": 0,
        "code_insee_commune": "75056",
        "synthese_entretien": "Recherche active",
    }


def test_predict_accepts_usager_id_but_excludes_it_from_model_features(monkeypatch) -> None:
    monkeypatch.setattr(api_main, "PIPELINE", FakePipeline([[0.05, 0.15, 0.80]]))
    monkeypatch.setattr(api_main, "model_version", lambda: "xgb-s1-test")

    response = client.post("/predict", json=_valid_payload())

    assert response.status_code == 200
    data = response.json()
    assert data["prediction"] == 2
    assert data["status"] == "ok"
    assert data["model_version"] == "xgb-s1-test"
    assert data["request_id"].startswith("req_")


def test_predict_returns_a_revoir_below_confidence_threshold(monkeypatch) -> None:
    monkeypatch.setattr(api_main, "PIPELINE", FakePipeline([[0.40, 0.35, 0.25]]))
    monkeypatch.setattr(api_main, "ABSTENTION_THRESHOLD", 0.50)
    monkeypatch.setattr(api_main, "model_version", lambda: "xgb-s1-test")

    response = client.post("/predict", json=_valid_payload())

    assert response.status_code == 200
    data = response.json()
    assert data["prediction"] == 0
    assert data["status"] == "a_revoir"
