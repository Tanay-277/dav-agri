from __future__ import annotations

from database.connection import get_connection
from database.repositories.base import BaseRepository


class InsightRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(table_name="insights", pk_field="insight_id")

    def bulk_insert(self, records: list[dict]) -> int:
        if not records:
            return 0
        columns = list(records[0].keys())
        placeholders = ", ".join(["?"] * len(columns))
        sql = f"INSERT INTO insights ({', '.join(columns)}) VALUES ({placeholders})"
        conn = get_connection()
        try:
            cur = conn.executemany(sql, [tuple(r[c] for c in columns) for r in records])
            conn.commit()
            return cur.rowcount
        finally:
            conn.close()

    def get_by_query(self, query_id: int) -> list[dict]:
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM insights WHERE query_id = ? ORDER BY created_at ASC",
                (query_id,),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def get_by_location(self, location_id: str, limit: int = 100) -> list[dict]:
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM insights WHERE location_id = ? ORDER BY created_at DESC LIMIT ?",
                (location_id, limit),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()
