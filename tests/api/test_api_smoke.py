from __future__ import annotations

import json

from fastapi.testclient import TestClient

from src.api.main import app
import src.api.main as api_main

client = TestClient(app)


def test_root_serves_ui_page() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Portfolio ML Ops" in response.text


def test_health_endpoint_returns_ok_payload() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "model_loaded" in data
    assert "model_version" in data


def test_predict_returns_503_when_model_not_trained(monkeypatch) -> None:
    # Force deterministic behavior independent from local artifact state.
    monkeypatch.setattr(api_main, "PIPELINE", None)

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


def test_predict_rejects_unknown_payload_field() -> None:
    payload = {
        "age": 35,
        "niveau_diplome": "Bac",
        "anciennete_poste_ans": 4.0,
        "code_rome_vise": "M1602",
        "est_allocataire": 1,
        "nationalite_hors_ue": 0,
        "departement_insee": "75",
        "synthese_entretien": "Recherche active",
        "unexpected_field": "forbidden",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_retrain_endpoint_returns_ok_with_mocked_training(monkeypatch) -> None:
    def fake_train_and_save_model(csv_path=None, **kwargs):
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


def test_history_returns_recent_prediction_events(monkeypatch, tmp_path) -> None:
    history_path = tmp_path / "predict_history.jsonl"
    events = [
        {
            "timestamp_utc": "2026-07-29T10:00:00+00:00",
            "request_id": "req_001",
            "output": {"prediction": 1, "confidence": 0.71, "status": "ok"},
        },
        {
            "timestamp_utc": "2026-07-29T10:01:00+00:00",
            "request_id": "req_002",
            "output": {
                "prediction": 2,
                "confidence": 0.42,
                "status": "a_revoir",
            },
        },
    ]
    history_path.write_text(
        "\n".join(json.dumps(event) for event in events), encoding="utf-8"
    )
    monkeypatch.setattr(api_main, "PREDICT_LOG_PATH", history_path)

    response = client.get("/history?limit=1")

    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["items"][0]["request_id"] == "req_002"


def test_train_alias_removed_returns_404() -> None:
    response = client.post("/train", json={"trigger": "test"})
    assert response.status_code == 404
