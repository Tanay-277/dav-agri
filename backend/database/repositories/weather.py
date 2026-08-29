from __future__ import annotations

from database.connection import get_connection
from database.repositories.base import BaseRepository


class WeatherRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(table_name="weather_observations", pk_field="observation_id")

    def bulk_insert(self, records: list[dict]) -> int:
        if not records:
            return 0
        columns = list(records[0].keys())
        placeholders = ", ".join(["?"] * len(columns))
        sql = f"INSERT OR IGNORE INTO weather_observations ({', '.join(columns)}) VALUES ({placeholders})"
        conn = get_connection()
        try:
            cur = conn.executemany(sql, [tuple(r[c] for c in columns) for r in records])
            conn.commit()
            return cur.rowcount
        finally:
            conn.close()

    def get_current(self, location_id: str) -> dict | None:
        conn = get_connection()
        try:
            row = conn.execute(
                """
                SELECT * FROM weather_observations
                WHERE location_id = ? AND data_classification IN ('current', 'historical')
                ORDER BY timestamp DESC LIMIT 1
                """,
                (location_id,),
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_forecast(self, location_id: str, days: int = 3) -> list[dict]:
        conn = get_connection()
        try:
            rows = conn.execute(
                """
                SELECT * FROM weather_observations
                WHERE location_id = ? AND data_classification = 'forecast'
                ORDER BY timestamp ASC LIMIT ?
                """,
                (location_id, days),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def get_historical(
        self,
        location_id: str,
        start: str | None = None,
        end: str | None = None,
    ) -> list[dict]:
        sql = "SELECT * FROM weather_observations WHERE location_id = ? AND data_classification = 'historical'"
        params: list = [location_id]
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

    def get_rainfall_trends(self, location_id: str, start: str, end: str) -> list[dict]:
        conn = get_connection()
        try:
            rows = conn.execute(
                """
                SELECT record_date, SUM(rainfall_mm) as total_rainfall,
                       AVG(rainfall_mm) as avg_rainfall
                FROM weather_observations
                WHERE location_id = ? AND record_date BETWEEN ? AND ?
                GROUP BY record_date ORDER BY record_date ASC
                """,
                (location_id, start, end),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def get_temperature_trends(
        self, location_id: str, start: str, end: str
    ) -> list[dict]:
        conn = get_connection()
        try:
            rows = conn.execute(
                """
                SELECT record_date, AVG(temperature_c) as avg_temp,
                       MIN(temperature_c) as min_temp, MAX(temperature_c) as max_temp
                FROM weather_observations
                WHERE location_id = ? AND record_date BETWEEN ? AND ?
                GROUP BY record_date ORDER BY record_date ASC
                """,
                (location_id, start, end),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def compare_locations(
        self,
        location_ids: list[str],
        metric: str,
        start: str,
        end: str,
    ) -> list[dict]:
        placeholders = ",".join(["?"] * len(location_ids))
        sql = f"""
            SELECT location_id, record_date, AVG({metric}) as value
            FROM weather_observations
            WHERE location_id IN ({placeholders})
            AND record_date BETWEEN ? AND ?
            GROUP BY location_id, record_date
            ORDER BY location_id, record_date ASC
        """
        params = location_ids + [start, end]
        conn = get_connection()
        try:
            rows = conn.execute(sql, tuple(params)).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()
