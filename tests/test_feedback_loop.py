"""Tests pour les endpoints de feedback et la politique de promotion."""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.api.feedback_store import FeedbackStore
from scripts.promotion import decide_promotion

client = TestClient(app)


def _make_prediction() -> str:
    """Effectue une vraie prédiction et retourne son request_id (pour /feedback)."""
    response = client.post(
        "/predict",
        json={"synthese_entretien": "Profil autonome, recherche active."},
    )
    assert response.status_code == 200
    return response.json()["request_id"]


class TestPromotionPolicy:
    """Tests de la politique de promotion (fonction pure)."""

    def test_promotion_candidate_wins_all(self):
        """Candidat meilleur partout → promotion."""
        prod = {"f1_macro": 0.6138, "recall_class_2": 0.6426}
        cand = {"f1_macro": 0.6200, "recall_class_2": 0.6600}
        decision = decide_promotion(cand, prod)
        assert decision.promote is True
        assert "recall_class_2" in decision.reason

    def test_promotion_candidate_wins_recall_loses_f1(self):
        """Candidat meilleur sur recall_class_2, pire sur f1 → accepté."""
        prod = {"f1_macro": 0.6138, "recall_class_2": 0.6426}
        cand = {"f1_macro": 0.6070, "recall_class_2": 0.6540}  # F1 -0.68%, Recall +1.14%
        decision = decide_promotion(cand, prod)
        assert decision.promote is True
        assert "f1_macro" in decision.reason

    def test_promotion_candidate_loses_recall(self):
        """Candidat pire sur recall_class_2 → rejet."""
        prod = {"f1_macro": 0.6138, "recall_class_2": 0.6426}
        cand = {"f1_macro": 0.6200, "recall_class_2": 0.6350}  # Recall -0.76%
        decision = decide_promotion(cand, prod)
        assert decision.promote is False

    def test_promotion_candidate_identical(self):
        """Candidat identique → accepté (pas de régression)."""
        prod = {"f1_macro": 0.6138, "recall_class_2": 0.6426}
        cand = {"f1_macro": 0.6138, "recall_class_2": 0.6426}
        decision = decide_promotion(cand, prod)
        assert decision.promote is True

    def test_promotion_candidate_worse_everywhere(self):
        """Candidat pire partout → rejet."""
        prod = {"f1_macro": 0.6138, "recall_class_2": 0.6426}
        cand = {"f1_macro": 0.6000, "recall_class_2": 0.6300}
        decision = decide_promotion(cand, prod)
        assert decision.promote is False

    def test_promotion_reason_is_explicable(self):
        """La raison de la décision doit être compréhensible sans le code."""
        prod = {"f1_macro": 0.6138, "recall_class_2": 0.6426}
        cand = {"f1_macro": 0.6070, "recall_class_2": 0.6540}
        decision = decide_promotion(cand, prod)
        assert "recall_class_2" in decision.reason
        assert "PROMU" in decision.reason or "REJETÉ" in decision.reason
        assert any(c.isdigit() for c in decision.reason)


class TestFeedbackEndpoint:
    """Tests de l'endpoint /feedback."""

    def test_feedback_post_valid(self):
        """POST /feedback pour une prédiction réellement loguée → 201."""
        request_id = _make_prediction()
        response = client.post(
            "/feedback",
            json={"request_id": request_id, "true_label": 1, "comments": "Test feedback"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "stored"
        assert data["feedback_id"] == request_id

    def test_feedback_post_unknown_request_id(self):
        """POST /feedback avec un request_id jamais prédit → 404."""
        response = client.post(
            "/feedback",
            json={"request_id": "req_never_predicted_xyz", "true_label": 1},
        )
        assert response.status_code == 404

    def test_feedback_post_invalid_label(self):
        """POST /feedback avec un label invalide → 422 (Pydantic)."""
        request_id = _make_prediction()
        response = client.post(
            "/feedback",
            json={"request_id": request_id, "true_label": 5},  # Hors {0,1,2}
        )
        assert response.status_code == 422

    def test_feedback_idempotent(self):
        """Envoyer deux fois le même feedback → idempotent (201 dans les deux cas)."""
        request_id = _make_prediction()
        payload = {"request_id": request_id, "true_label": 0}
        response1 = client.post("/feedback", json=payload)
        response2 = client.post("/feedback", json=payload)
        assert response1.status_code == 201
        assert response2.status_code == 201

    def test_feedback_conflict(self):
        """Feedback contradictoire (même request_id, label différent) → 409."""
        request_id = _make_prediction()
        client.post("/feedback", json={"request_id": request_id, "true_label": 0})
        response = client.post("/feedback", json={"request_id": request_id, "true_label": 1})
        assert response.status_code == 409
        assert "conflictuel" in response.json()["detail"].lower()

    def test_feedback_count(self):
        """GET /feedback/count retourne total et nouveaux."""
        for _ in range(3):
            request_id = _make_prediction()
            client.post("/feedback", json={"request_id": request_id, "true_label": 0})

        response = client.get("/feedback/count")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 3
        assert data["new"] >= 3

    def test_feedback_health(self):
        """GET /feedback/health retourne le statut."""
        response = client.get("/feedback/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "total_feedbacks" in data
        assert "unconsumed_feedbacks" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
