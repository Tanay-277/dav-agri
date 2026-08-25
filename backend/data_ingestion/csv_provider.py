from __future__ import annotations

from typing import Any

import pandas as pd

from core.logging import get_logger
from data_ingestion.base import BaseProvider, WeatherRecord

logger = get_logger(__name__)

# Map normalized CSV columns to WeatherRecord fields.
_WEATHER_COLUMNS = {
    "rainfall": "rainfall_mm",
    "temperature": "temperature_c",
    "humidity": "humidity_pct",
    "soil_moisture": "soil_moisture_pct",
}

# Columns that are agricultural, not weather.
_AGRICULTURAL_COLUMNS = {
    "crop",
    "state",
    "district",
    "date",
    "yield",
    "production",
    "area",
    "fertilizer",
    "irrigation",
}


class CSVProvider(BaseProvider):
    """Provider that reads from the existing CSV dataset."""

    name = "csv"

    def __init__(self) -> None:
        self._df: pd.DataFrame | None = None

    def _load(self) -> pd.DataFrame:
        if self._df is None:
            from database.data import _load_dataset

            raw = _load_dataset()
            if raw.empty:
                self._df = raw
                return self._df

            self._df = raw.copy()

            # Build location_id if not present.
            if "location_id" not in self._df.columns:
                if "state" in self._df.columns and "district" in self._df.columns:
                    self._df["location_id"] = (
                        self._df["state"]
                        .fillna("")
                        .astype(str)
                        .str.strip()
                        .str.lower()
                        .str.replace(" ", "_")
                        + "_"
                        + self._df["district"]
                        .fillna("")
                        .astype(str)
                        .str.strip()
                        .str.lower()
                        .str.replace(" ", "_")
                    )
                else:
                    self._df["location_id"] = "unknown"

        return self._df

    def fetch_historical(
        self,
        location_id: str,
        latitude: float | None,
        longitude: float | None,
        start_date: str,
        end_date: str,
    ) -> list[WeatherRecord]:
        df = self._load()
        if df.empty:
            return []

        mask = pd.Series([True] * len(df), index=df.index)
        if location_id and location_id != "unknown":
            mask = mask & (df["location_id"] == location_id)
        if "date" in df.columns:
            start = pd.to_datetime(start_date, errors="coerce")
            end = pd.to_datetime(end_date, errors="coerce")
            if pd.notna(start):
                mask = mask & (df["date"] >= start)
            if pd.notna(end):
                mask = mask & (df["date"] <= end)

        sub = df[mask].copy()
        if sub.empty:
            return []

        records: list[WeatherRecord] = []
        for _, row in sub.iterrows():
            ts = row.get("date")
            if pd.isna(ts):
                continue
            records.append(
                WeatherRecord(
                    timestamp=pd.Timestamp(ts).to_pydatetime(),
                    location_id=str(row.get("location_id", location_id)),
                    latitude=latitude,
                    longitude=longitude,
                    rainfall_mm=_safe_float(row.get("rainfall")),
                    temperature_c=_safe_float(row.get("temperature")),
                    humidity_pct=_safe_float(row.get("humidity")),
                    soil_moisture_pct=_safe_float(row.get("soil_moisture")),
                    wind_speed_kmh=None,
                    cloud_cover_okta=None,
                    precipitation_probability_pct=None,
                    source="csv",
                    raw=row.to_dict(),
                )
            )
        return records

    def fetch_current(
        self,
        location_id: str,
        latitude: float | None,
        longitude: float | None,
    ) -> WeatherRecord | None:
        records = self.fetch_historical(
            location_id, latitude, longitude, "1900-01-01", "2100-01-01"
        )
        if not records:
            return None
        return max(records, key=lambda r: r.timestamp)

    def as_dataframe(self, records: list[WeatherRecord]) -> pd.DataFrame:
        """Convert weather records to a DataFrame for merging with agricultural data."""
        if not records:
            return pd.DataFrame(
                columns=[
                    "timestamp",
                    "location_id",
                    "latitude",
                    "longitude",
                    "rainfall_mm",
                    "temperature_c",
                    "humidity_pct",
                    "soil_moisture_pct",
                    "wind_speed_kmh",
                    "cloud_cover_okta",
                    "precipitation_probability_pct",
                    "source",
                ]
            )
        data = [r.model_dump() for r in records]
        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["timestamp"]).dt.date
        return df


def _safe_float(value: Any) -> float | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    try:
        f = float(value)
        return None if pd.isna(f) else f
    except (TypeError, ValueError):
        return None
