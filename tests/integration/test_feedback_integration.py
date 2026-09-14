"""Test d'intégration complet de la boucle de feedback."""

import time

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.api.feedback_store import FeedbackStore
from scripts.promotion import decide_promotion
from scripts import retrain_feedback

client = TestClient(app)


def _make_prediction() -> str:
    response = client.post(
        "/predict",
        json={"synthese_entretien": "Profil autonome, recherche active."},
    )
    assert response.status_code == 200
    return response.json()["request_id"]


class TestFeedbackLoopIntegration:
    """Test de la boucle complète : feedback → stockage → décision de promotion."""

    def test_complete_feedback_loop_scenario(self):
        """Scénario complet : prédire, annoter, vérifier stockage et consommation."""

        response = client.get("/feedback/health")
        assert response.status_code == 200

        feedback_ids = [_make_prediction() for _ in range(5)]
        for i, request_id in enumerate(feedback_ids):
            response = client.post(
                "/feedback",
                json={"request_id": request_id, "true_label": i % 3, "comments": f"Test #{i}"},
            )
            assert response.status_code == 201

        response = client.get("/feedback/count")
        assert response.status_code == 200
        data = response.json()
        assert data["new"] >= 5

        # Conflit : même request_id, label différent
        response = client.post(
            "/feedback", json={"request_id": feedback_ids[0], "true_label": (0 % 3 + 1) % 3}
        )
        assert response.status_code == 409

        # Idempotence : même request_id, même label
        response = client.post("/feedback", json={"request_id": feedback_ids[0], "true_label": 0})
        assert response.status_code == 201

        store = FeedbackStore()
        unconsumed = store.load_unconsumed()
        assert len(unconsumed) >= 5

        store.mark_as_used(feedback_ids)
        response = client.get("/feedback/count")
        data_after_mark = response.json()
        assert data_after_mark["new"] <= data["new"] - 5

    def test_promotion_decision_integration(self):
        """Décision de promotion sur des métriques réalistes (recall_class_2 critique)."""
        prod_metrics = {"f1_macro": 0.6138, "recall_class_2": 0.6426}
        cand_metrics = {"f1_macro": 0.6070, "recall_class_2": 0.6540}

        decision = decide_promotion(cand_metrics, prod_metrics)
        assert decision.promote is True
        assert "recall_class_2" in decision.reason
        assert "PROMU" in decision.reason

        cand_pire = {"f1_macro": 0.6200, "recall_class_2": 0.6350}
        decision_reject = decide_promotion(cand_pire, prod_metrics)
        assert decision_reject.promote is False
        assert "REJETÉ" in decision_reject.reason

    def test_retrain_skip_below_threshold(self):
        """retrain_feedback sort en succès (0) si le seuil n'est pas atteint."""
        exit_code = retrain_feedback.retrain_with_feedbacks(min_feedback=10_000_000)
        assert exit_code == 0

    def test_join_feedbacks_to_features(self):
        """La jointure feedback ⋈ logs de prédiction retrouve les bonnes features."""
        request_id = _make_prediction()
        client.post("/feedback", json={"request_id": request_id, "true_label": 1})

        log_inputs = retrain_feedback.load_predict_log_inputs()
        assert request_id in log_inputs

        feedbacks = [{"request_id": request_id, "true_label": 1}]
        joined_df, joined_ids = retrain_feedback.join_feedbacks_to_features(feedbacks, log_inputs)
        assert request_id in joined_ids
        assert len(joined_df) == 1
        assert joined_df.iloc[0]["classe_retour_emploi"] == 1

    def test_ensure_reference_set_is_stable(self):
        """Le reference_set est créé une fois puis reste identique entre deux appels."""
        ref1 = retrain_feedback.ensure_reference_set()
        ref2 = retrain_feedback.ensure_reference_set()
        assert len(ref1) == len(ref2)
        assert list(ref1.columns) == list(ref2.columns)

    def test_run_retrain_cycle_skips_without_feedback_or_dataset(self, tmp_path, monkeypatch):
        """Un déclenchement manuel sans nouveau feedback ni dataset_path est ignoré (pas d'entraînement inutile)."""
        empty_log_path = tmp_path / "empty_predict_log.jsonl"
        monkeypatch.setattr(retrain_feedback, "PREDICT_LOG_PATH", empty_log_path)
        monkeypatch.setattr(
            retrain_feedback.FeedbackStore, "load_unconsumed", lambda self: []
        )

        result = retrain_feedback.run_retrain_cycle(
            min_feedback=0, dataset_path=None, trigger="test_no_feedback"
        )
        assert result["status"] == "skipped"
        assert "aucun nouveau feedback" in result["reason"]

    def test_sample_size_guard_downgrades_promotion_below_threshold(self):
        """Une promotion est rétrogradée en rejet si trop peu de feedbacks l'appuient (bruit statistique)."""
        from scripts.promotion import PromotionDecision

        would_promote = PromotionDecision(promote=True, reason="✓ recall_class_2: gain\n→ PROMU")

        guarded = retrain_feedback.apply_sample_size_guard(would_promote, joined_count=5)
        assert guarded.promote is False
        assert "Promotion annulée par prudence" in guarded.reason

        not_guarded = retrain_feedback.apply_sample_size_guard(
            would_promote, joined_count=retrain_feedback.MIN_FEEDBACK_FOR_PROMOTION
        )
        assert not_guarded.promote is True

    def test_sample_size_guard_leaves_rejection_untouched(self):
        """Un rejet reste un rejet quel que soit le nombre de feedbacks joints."""
        from scripts.promotion import PromotionDecision

        rejected = PromotionDecision(promote=False, reason="→ REJETÉ")
        guarded = retrain_feedback.apply_sample_size_guard(rejected, joined_count=0)
        assert guarded is rejected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
