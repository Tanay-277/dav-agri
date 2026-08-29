from __future__ import annotations

from database.connection import get_connection
from database.repositories.base import BaseRepository


class LocationRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(table_name="locations", pk_field="location_id")

    def upsert(self, data: dict) -> str:
        location_id = data["location_id"]
        existing = self.find_by_id(location_id)
        if existing:
            self.update(location_id, data)
        else:
            self.insert(data)
        return location_id

    def find_by_state(self, state: str) -> list[dict]:
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM locations WHERE state = ? ORDER BY district ASC",
                (state,),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def find_by_district(self, district: str) -> list[dict]:
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM locations WHERE district = ? ORDER BY state ASC",
                (district,),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def search(
        self, state: str | None = None, district: str | None = None
    ) -> list[dict]:
        sql = "SELECT * FROM locations WHERE 1=1"
        params: list = []
        if state:
            sql += " AND state = ?"
            params.append(state)
        if district:
            sql += " AND district = ?"
            params.append(district)
        sql += " ORDER BY state, district"
        conn = get_connection()
        try:
            rows = conn.execute(sql, tuple(params)).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()
