from __future__ import annotations

import json
from pathlib import Path

from core.logging import get_logger
from database.connection import _get_db_path, get_connection
from database.exceptions import MigrationError

logger = get_logger(__name__)


def init_db() -> None:
    """Apply pending migrations and ensure schema exists."""
    _run_migrations()
    logger.info("Database initialised at %s", _get_db_path())


def _run_migrations() -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                applied_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        applied = {
            row[0]
            for row in conn.execute("SELECT version FROM schema_migrations").fetchall()
        }
        migration_dir = Path(__file__).parent / "migrations"
        for file in sorted(migration_dir.glob("*.sql")):
            version = int(file.stem.split("_")[0])
            if version in applied:
                continue
            sql = file.read_text()
            up_section = sql.split("-- UP")[1].split("-- DOWN")[0].strip()
            try:
                conn.executescript(up_section)
                conn.execute(
                    "INSERT INTO schema_migrations (version) VALUES (?)", (version,)
                )
                conn.commit()
                logger.info("Applied migration %s", file.name)
            except Exception as exc:
                conn.rollback()
                raise MigrationError(
                    f"Failed to apply migration {file.name}: {exc}"
                ) from exc
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Legacy functions (preserved for backward compatibility with existing API routes)
# ---------------------------------------------------------------------------


def record_insight_run(filters: dict, insights: list, story: str = "") -> None:
    """Persist an insight run for history/reporting."""
    try:
        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO insight_history (filters_json, insights_json, story) "
                "VALUES (?, ?, ?)",
                (json.dumps(filters), json.dumps(insights), story),
            )
            conn.commit()
        finally:
            conn.close()
    except Exception as exc:  # pragma: no cover
        logger.warning("Failed to record insight run: %s", exc)


def set_meta(key: str, value: str) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO dataset_meta (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )
        conn.commit()
    finally:
        conn.close()


def record_task_log(task: dict) -> None:
    try:
        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO task_logs (task_id, condition, user_id, completed, duration_ms, voice_used, error) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    task.get("task_id"),
                    task.get("condition"),
                    task.get("user_id"),
                    1 if task.get("completed") else 0,
                    task.get("duration_ms"),
                    1 if task.get("voice_used") else 0,
                    task.get("error"),
                ),
            )
            conn.commit()
        finally:
            conn.close()
    except Exception as exc:  # pragma: no cover
        logger.warning("Failed to record task log: %s", exc)


def record_survey_response(survey: dict) -> None:
    try:
        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO survey_responses (task_id, condition, user_id, comprehension_score, trust_score, sus_score, feedback) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    survey.get("task_id"),
                    survey.get("condition"),
                    survey.get("user_id"),
                    survey.get("comprehension_score"),
                    survey.get("trust_score"),
                    survey.get("sus_score"),
                    survey.get("feedback"),
                ),
            )
            conn.commit()
        finally:
            conn.close()
    except Exception as exc:  # pragma: no cover
        logger.warning("Failed to record survey response: %s", exc)


init_db()
