"""Tests de l'historique de modèles et du rollback."""

import shutil

import joblib
import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.config import BEST_MODEL_DIR, BEST_MODEL_METADATA_PATH, BEST_MODEL_PATH
from scripts.retrain_feedback import (
    MODEL_HISTORY_DIR,
    list_model_history,
    rollback_model,
)

client = TestClient(app)


@pytest.fixture
def isolated_model_dir(tmp_path, monkeypatch):
    """Copie le modèle réel dans un répertoire jetable pour ne pas polluer models/best_model."""
    fake_dir = tmp_path / "best_model"
    fake_dir.mkdir()
    fake_model_path = fake_dir / "model.joblib"
    fake_metadata_path = fake_dir / "metadata.json"
    shutil.copy(BEST_MODEL_PATH, fake_model_path)
    shutil.copy(BEST_MODEL_METADATA_PATH, fake_metadata_path)

    import scripts.retrain_feedback as rf

    monkeypatch.setattr(rf, "BEST_MODEL_DIR", fake_dir)
    monkeypatch.setattr(rf, "BEST_MODEL_PATH", fake_model_path)
    monkeypatch.setattr(rf, "BEST_MODEL_METADATA_PATH", fake_metadata_path)
    monkeypatch.setattr(rf, "MODEL_HISTORY_DIR", fake_dir / "history")

    return fake_dir


class TestModelHistoryAndRollback:
    def test_no_history_returns_empty_list(self, isolated_model_dir):
        assert list_model_history() == []

    def test_rollback_without_history_raises(self, isolated_model_dir):
        with pytest.raises(FileNotFoundError):
            rollback_model()

    def test_archive_then_rollback_restores_previous_model(self, isolated_model_dir):
        import scripts.retrain_feedback as rf

        original_model = joblib.load(rf.BEST_MODEL_PATH)

        # Simule une promotion : archive le modèle courant puis écrit un "nouveau".
        rf._archive_current_model(reason="test_promotion")
        joblib.dump(original_model, rf.BEST_MODEL_PATH)  # "nouveau" modèle (même objet ici)

        history = list_model_history()
        assert len(history) == 1
        assert history[0]["archive_reason"] == "test_promotion"

        info = rollback_model()
        assert info["restored_timestamp"] == history[0]["timestamp"]

        # Le rollback lui-même archive l'état "nouveau" avant de restaurer : 2 entrées désormais.
        assert len(list_model_history()) == 2

    def test_rollback_unknown_timestamp_raises(self, isolated_model_dir):
        import scripts.retrain_feedback as rf

        rf._archive_current_model(reason="test")
        with pytest.raises(FileNotFoundError):
            rollback_model(timestamp="does-not-exist")

    def test_history_is_pruned_beyond_limit(self, isolated_model_dir, monkeypatch):
        import scripts.retrain_feedback as rf

        monkeypatch.setattr(rf, "MODEL_HISTORY_LIMIT", 2)
        for _ in range(4):
            rf._archive_current_model(reason="test_prune")

        assert len(list_model_history()) == 2


class TestRollbackEndpoints:
    def test_models_history_endpoint(self):
        response = client.get("/models/history")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "items" in data

    def test_rollback_endpoint_404_without_history(self, isolated_model_dir):
        response = client.post("/rollback", json={})
        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
