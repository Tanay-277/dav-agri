from __future__ import annotations

import sqlite3
from pathlib import Path

from core.config import get_settings
from core.logging import get_logger

logger = get_logger(__name__)

_DB_PATH = Path(get_settings().DATABASE_URL.replace("sqlite:///", ""))


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection with row access by name."""
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create tables if they do not exist. Idempotent on startup."""
    conn = get_connection()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS insight_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                filters_json TEXT NOT NULL,
                insights_json TEXT NOT NULL,
                story TEXT NOT NULL DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS dataset_meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            """
        )
        conn.commit()
    finally:
        conn.close()
    logger.info("Database initialised at %s", _DB_PATH)


def record_insight_run(filters: dict, insights: list, story: str = "") -> None:
    """Persist an insight run for history/reporting."""
    import json

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
    except Exception as exc:  # pragma: no cover - never break the request
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


# Ensure schema exists on import so data modules are safe regardless of
# whether the FastAPI lifespan has run yet (e.g. tests / worker warmup).
init_db()
