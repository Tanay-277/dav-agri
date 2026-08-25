from __future__ import annotations

from database.connection import get_connection
from database.repositories.base import BaseRepository


class AgriculturalRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(table_name="agricultural_records", pk_field="ag_record_id")

    def bulk_insert(self, records: list[dict]) -> int:
        if not records:
            return 0
        columns = list(records[0].keys())
        placeholders = ", ".join(["?"] * len(columns))
        sql = f"INSERT OR IGNORE INTO agricultural_records ({', '.join(columns)}) VALUES ({placeholders})"
        conn = get_connection()
        try:
            cur = conn.executemany(sql, [tuple(r[c] for c in columns) for r in records])
            conn.commit()
            return cur.rowcount
        finally:
            conn.close()

    def get_by_crop(
        self, crop: str, start: str | None = None, end: str | None = None
    ) -> list[dict]:
        sql = "SELECT * FROM agricultural_records WHERE crop = ?"
        params: list = [crop]
        if start:
            sql += " AND record_date >= ?"
            params.append(start)
        if end:
            sql += " AND record_date <= ?"
            params.append(end)
        sql += " ORDER BY record_date ASC"
        conn = get_connection()
        try:
            rows = conn.execute(sql, tuple(params)).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def get_crop_summary(self, crop: str, start: str, end: str) -> dict | None:
        conn = get_connection()
        try:
            row = conn.execute(
                """
                SELECT crop,
                       AVG(yield_kg_per_ha) as avg_yield,
                       SUM(production_tonnes) as total_production,
                       AVG(area_ha) as avg_area,
                       COUNT(*) as record_count
                FROM agricultural_records
                WHERE crop = ? AND record_date BETWEEN ? AND ?
                GROUP BY crop
                """,
                (crop, start, end),
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
