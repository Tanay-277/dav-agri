from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from core.config import get_settings


def _get_db_path() -> Path:
    return Path(get_settings().DATABASE_URL.replace("sqlite:///", ""))


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection with sensible pragmas."""
    conn = sqlite3.connect(_get_db_path(), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA cache_size=-64000")
    return conn


@contextmanager
def get_cursor() -> Generator[sqlite3.Cursor, None, None]:
    conn = get_connection()
    try:
        yield conn.cursor()
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
