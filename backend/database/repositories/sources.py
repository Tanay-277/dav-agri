from __future__ import annotations

from database.connection import get_connection
from database.repositories.base import BaseRepository


class DataSourceRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(table_name="data_sources", pk_field="source_id")

    def upsert(self, data: dict) -> str:
        source_id = data["source_id"]
        existing = self.find_by_id(source_id)
        if existing:
            self.update(source_id, data)
        else:
            self.insert(data)
        return source_id

    def get_active(self) -> list[dict]:
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM data_sources WHERE is_active = 1 ORDER BY name ASC"
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def deactivate(self, source_id: str) -> bool:
        conn = get_connection()
        try:
            cur = conn.execute(
                "UPDATE data_sources SET is_active = 0 WHERE source_id = ?",
                (source_id,),
            )
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()
