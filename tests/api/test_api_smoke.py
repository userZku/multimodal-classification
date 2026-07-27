from __future__ import annotations

from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_health_endpoint_returns_ok_payload() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "model_loaded" in data
    assert "model_version" in data


def test_predict_returns_503_when_model_not_trained() -> None:
    payload = {
        "age": 35,
        "niveau_diplome": "Bac",
        "anciennete_poste_ans": 4.0,
        "code_rome_vise": "M1602",
        "est_allocataire": 1,
        "nationalite_hors_ue": 0,
        "departement_insee": "75",
        "synthese_entretien": "Recherche active",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 503
