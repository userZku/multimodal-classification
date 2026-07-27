from __future__ import annotations

from fastapi.testclient import TestClient

from src.api.main import app
import src.api.main as api_main


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


def test_retrain_endpoint_returns_ok_with_mocked_training(monkeypatch) -> None:
    def fake_train_and_save_model(csv_path=None):
        return {
            "metrics": {
                "accuracy": 0.75,
                "f1_macro": 0.72,
                "recall_class_2": 0.54,
            }
        }

    monkeypatch.setattr(api_main, "train_and_save_model", fake_train_and_save_model)
    monkeypatch.setattr(api_main, "reload_artifacts", lambda: None)

    response = client.post("/retrain", json={"trigger": "test"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "event_id" in data
    assert "metrics" in data
