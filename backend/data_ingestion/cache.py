from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Any

from core.config import get_settings
from core.logging import get_logger

logger = get_logger(__name__)

_DB_PATH = None


def _get_db_path() -> str:
    global _DB_PATH
    if _DB_PATH is None:
        _DB_PATH = get_settings().DATABASE_URL.replace("sqlite:///", "")
    return _DB_PATH


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(_get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_cache() -> None:
    """Create weather API cache table if it does not exist."""
    conn = _get_connection()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS weather_api_cache (
                provider TEXT NOT NULL,
                location_id TEXT NOT NULL,
                date TEXT NOT NULL,
                payload TEXT NOT NULL,
                fetched_at TEXT NOT NULL DEFAULT (datetime('now')),
                PRIMARY KEY (provider, location_id, date)
            );
            CREATE INDEX IF NOT EXISTS idx_weather_cache_provider_loc
                ON weather_api_cache (provider, location_id);
            CREATE INDEX IF NOT EXISTS idx_weather_cache_fetched_at
                ON weather_api_cache (fetched_at);
            """
        )
        conn.commit()
    finally:
        conn.close()
    logger.info("Weather API cache table initialised at %s", _get_db_path())


def get_cached(
    provider: str,
    location_id: str,
    date: str,
    ttl_hours: int,
) -> dict[str, Any] | None:
    """Return cached payload if fresh, else None."""
    conn = _get_connection()
    try:
        row = conn.execute(
            "SELECT payload, fetched_at FROM weather_api_cache WHERE provider = ? AND location_id = ? AND date = ?",
            (provider, location_id, date),
        ).fetchone()
        if not row:
            return None
        fetched_at = datetime.fromisoformat(row["fetched_at"])
        if datetime.utcnow() - fetched_at > timedelta(hours=ttl_hours):
            return None
        return json.loads(row["payload"])
    finally:
        conn.close()


def set_cached(
    provider: str,
    location_id: str,
    date: str,
    payload: dict[str, Any],
) -> None:
    """Upsert a cached payload."""
    conn = _get_connection()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO weather_api_cache (provider, location_id, date, payload, fetched_at) "
            "VALUES (?, ?, ?, ?, datetime('now'))",
            (provider, location_id, date, json.dumps(payload)),
        )
        conn.commit()
    finally:
        conn.close()


def prune_stale(ttl_hours: int) -> int:
    """Delete stale cache entries. Returns number of rows deleted."""
    conn = _get_connection()
    try:
        if ttl_hours <= 0:
            cursor = conn.execute("DELETE FROM weather_api_cache")
        else:
            cursor = conn.execute(
                "DELETE FROM weather_api_cache WHERE datetime(fetched_at) < datetime('now', ?)",
                (f"-{ttl_hours} hours",),
            )
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()
