from __future__ import annotations

from database.connection import get_connection
from database.repositories.base import BaseRepository


class QueryLogRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(table_name="query_logs", pk_field="query_id")

    def get_recent(self, limit: int = 50) -> list[dict]:
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM query_logs ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def get_by_session(self, session_id: str) -> list[dict]:
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM query_logs WHERE session_id = ? ORDER BY created_at ASC",
                (session_id,),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()
