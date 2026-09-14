"""SQLite-backed store for prediction feedback used by the retraining loop."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from src.config import PROJECT_ROOT


class FeedbackStore:
    """CRUD helper for the `feedbacks` SQLite table."""

    def __init__(self, db_path: Path | str | None = None):
        self.db_path = Path(db_path) if db_path else PROJECT_ROOT / "data" / "feedbacks.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _init_schema(self) -> None:
        with sqlite3.connect(self.db_path) as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS feedbacks (
                    request_id TEXT PRIMARY KEY,
                    true_label INTEGER NOT NULL CHECK (true_label IN (0, 1, 2)),
                    comments TEXT,
                    created_at TEXT NOT NULL,
                    used_for_training INTEGER NOT NULL DEFAULT 0 CHECK (used_for_training IN (0, 1))
                )
                """
            )
            con.commit()

    def insert_or_conflict(
        self, request_id: str, true_label: int, comments: str | None = None
    ) -> tuple[str, int]:
        """Insert a feedback row; detect same-id/different-label conflicts.

        Returns (status, http_code) where status is 'created', 'already_exists'
        or 'conflict', matching http_code 201/201/409.
        """
        if true_label not in (0, 1, 2):
            raise ValueError(f"Label invalide: {true_label}. Attendu: 0, 1 ou 2")

        with sqlite3.connect(self.db_path) as con:
            row = con.execute(
                "SELECT true_label FROM feedbacks WHERE request_id = ?", (request_id,)
            ).fetchone()

            if row is None:
                created_at = datetime.now(tz=timezone.utc).isoformat()
                con.execute(
                    """
                    INSERT INTO feedbacks (request_id, true_label, comments, created_at, used_for_training)
                    VALUES (?, ?, ?, ?, 0)
                    """,
                    (request_id, true_label, comments, created_at),
                )
                con.commit()
                return "created", 201

            existing_label = row[0]
            if existing_label == true_label:
                return "already_exists", 201
            return "conflict", 409

    def get_count(self) -> dict[str, int]:
        with sqlite3.connect(self.db_path) as con:
            total = con.execute("SELECT COUNT(*) FROM feedbacks").fetchone()[0]
            new = con.execute(
                "SELECT COUNT(*) FROM feedbacks WHERE used_for_training = 0"
            ).fetchone()[0]
        return {"total": total, "new": new}

    def load_unconsumed(self) -> list[dict]:
        with sqlite3.connect(self.db_path) as con:
            con.row_factory = sqlite3.Row
            rows = con.execute(
                """
                SELECT request_id, true_label, comments, created_at
                FROM feedbacks
                WHERE used_for_training = 0
                ORDER BY created_at ASC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def mark_as_used(self, request_ids: list[str]) -> None:
        if not request_ids:
            return
        with sqlite3.connect(self.db_path) as con:
            placeholders = ", ".join("?" * len(request_ids))
            con.execute(
                f"UPDATE feedbacks SET used_for_training = 1 WHERE request_id IN ({placeholders})",
                request_ids,
            )
            con.commit()
