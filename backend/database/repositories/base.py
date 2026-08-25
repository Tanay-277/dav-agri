from __future__ import annotations

from typing import Any

from database.connection import get_connection


class BaseRepository:
    """Generic CRUD repository for a single table."""

    def __init__(self, table_name: str, pk_field: str = "id") -> None:
        self.table_name = table_name
        self.pk_field = pk_field

    def _execute_write(self, sql: str, params: tuple = ()) -> int:
        conn = get_connection()
        try:
            cur = conn.execute(sql, params)
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    def _execute_read(self, sql: str, params: tuple = ()) -> list[dict]:
        conn = get_connection()
        try:
            rows = conn.execute(sql, params).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def find_by_id(self, pk_value: Any) -> dict | None:
        sql = f"SELECT * FROM {self.table_name} WHERE {self.pk_field} = ?"
        rows = self._execute_read(sql, (pk_value,))
        return rows[0] if rows else None

    def find_all(
        self,
        filters: dict[str, Any] | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[dict], int]:
        base_sql = f"SELECT * FROM {self.table_name}"
        count_sql = f"SELECT COUNT(*) FROM {self.table_name}"
        params: list[Any] = []
        where_clauses: list[str] = []

        if filters:
            for key, value in filters.items():
                where_clauses.append(f"{key} = ?")
                params.append(value)

        if where_clauses:
            where_str = " WHERE " + " AND ".join(where_clauses)
            base_sql += where_str
            count_sql += where_str

        base_sql += f" ORDER BY {self.pk_field} DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        rows = self._execute_read(base_sql, tuple(params))
        count_rows = self._execute_read(count_sql, tuple(params[: len(where_clauses)]))
        count = count_rows[0][list(count_rows[0].keys())[0]] if count_rows else 0
        return rows, count

    def insert(self, data: dict) -> int:
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        sql = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        return self._execute_write(sql, tuple(data.values()))

    def update(self, pk_value: Any, data: dict) -> bool:
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        sql = f"UPDATE {self.table_name} SET {set_clause} WHERE {self.pk_field} = ?"
        params = tuple(data.values()) + (pk_value,)
        conn = get_connection()
        try:
            cur = conn.execute(sql, params)
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()

    def delete(self, pk_value: Any) -> bool:
        sql = f"DELETE FROM {self.table_name} WHERE {self.pk_field} = ?"
        conn = get_connection()
        try:
            cur = conn.execute(sql, (pk_value,))
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()

    def exists(self, pk_value: Any) -> bool:
        sql = f"SELECT 1 FROM {self.table_name} WHERE {self.pk_field} = ?"
        rows = self._execute_read(sql, (pk_value,))
        return len(rows) > 0
