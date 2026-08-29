from __future__ import annotations

from functools import lru_cache
from typing import Any

import pandas as pd

from core.config import get_settings
from core.logging import get_logger
from data_ingestion.errors import DataIngestionError
from data_ingestion.openmeteo_provider import OpenMeteoProvider
from data_ingestion.settings import get_data_ingestion_settings
from database.db import set_meta

logger = get_logger(__name__)

# Normalised column names -> list of accepted raw headers (lowercased).
COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
    "crop": ("crop", "crop_type", "cropname"),
    "state": ("state", "state_name", "region"),
    "district": ("district", "district_name"),
    "date": ("date", "date_of_record", "datetime"),
    "year": ("year", "crop_year", "season_year"),
    "rainfall": ("rainfall", "rain", "rainfall_mm", "precipitation"),
    "temperature": ("temperature", "temp", "temperature_c", "avg_temp"),
    "yield": ("yield", "yield_kg", "production_per_ha", "crop_yield"),
    "production": ("production", "production_tonnes", "output"),
    "humidity": ("humidity", "humidity_percent", "rh"),
    "soil_moisture": ("soil_moisture", "soil", "moisture", "soil_moisture_percent"),
    "area": ("area", "area_ha", "cropped_area"),
    "fertilizer": ("fertilizer", "fertilizer_kg", "fertiliser"),
    "irrigation": ("irrigation", "irrigation_area", "irrigated"),
}


def _normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename known columns to canonical names, drop unknown empties."""
    renamed: dict[str, str] = {}
    for col in df.columns:
        key = str(col).strip().lower().replace(" ", "_")
        for canonical, aliases in COLUMN_ALIASES.items():
            if key in aliases:
                renamed[col] = canonical
                break
    return df.rename(columns=renamed)


@lru_cache(maxsize=1)
def _load_dataset() -> pd.DataFrame:
    """Load and cache the dataset once. Returns empty df if missing."""
    settings = get_settings()
    path = settings.dataset_path

    if not path.exists():
        logger.warning("Dataset not found at %s. Returning empty frame.", path)
        set_meta("status", "missing")
        return pd.DataFrame()

    try:
        df = pd.read_csv(path)
    except Exception as exc:
        logger.error("Failed to parse dataset %s: %s", path, exc)
        set_meta("status", "error")
        return pd.DataFrame()

    df = _normalise_columns(df)

    # Light cleaning
    for col in (
        "rainfall",
        "temperature",
        "yield",
        "production",
        "humidity",
        "soil_moisture",
        "area",
    ):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    set_meta("status", "loaded")
    set_meta("rows", str(len(df)))
    set_meta("source", str(path))
    logger.info("Loaded dataset with %d rows from %s", len(df), path)
    return df


def get_dataset() -> pd.DataFrame:
    return _load_dataset()


def _resolve_location(
    filters: dict[str, Any] | None
) -> tuple[str, float | None, float | None]:
    """Return (location_id, latitude, longitude) from filters or dataset."""
    filters = filters or {}
    state = filters.get("state")
    district = filters.get("district")
    location_id = "unknown"
    if state and district:
        location_id = f"{str(state).strip().lower().replace(' ', '_')}_{str(district).strip().lower().replace(' ', '_')}"
    elif state:
        location_id = str(state).strip().lower().replace(" ", "_")

    # Try to resolve lat/lon from dataset if API provider is active.
    lat = filters.get("latitude")
    lon = filters.get("longitude")
    if lat is None or lon is None:
        df = get_dataset()
        if not df.empty and "state" in df.columns and "district" in df.columns:
            mask = pd.Series([True] * len(df), index=df.index)
            if state:
                mask = mask & (df["state"].astype(str) == str(state))
            if district:
                mask = mask & (df["district"].astype(str) == str(district))
            sub = df[mask]
            if not sub.empty:
                # Use the first match's approximate centroid (mean of available coords if any).
                # For CSV-only mode, lat/lon remain None.
                pass
    return location_id, lat, lon


def get_weather_data(filters: dict[str, Any] | None = None) -> pd.DataFrame:
    """Return weather data for the given filters using the active provider.

    - csv: returns weather columns from the local dataset.
    - open-meteo: fetches from API, normalizes, caches, and returns DataFrame.
    """
    settings = get_data_ingestion_settings()
    provider_name = settings.provider
    filters = filters or {}

    if provider_name == "csv":
        df = get_filtered(filters)
        weather_cols = [
            c
            for c in df.columns
            if c in ("rainfall", "temperature", "humidity", "soil_moisture")
        ]
        if not weather_cols:
            return pd.DataFrame(
                columns=[
                    "timestamp",
                    "location_id",
                    "rainfall_mm",
                    "temperature_c",
                    "humidity_pct",
                    "soil_moisture_pct",
                    "source",
                ]
            )
        out = df[weather_cols].copy()
        out["timestamp"] = df.get("date", pd.NaT)
        out["location_id"] = _resolve_location(filters)[0]
        out["source"] = "csv"
        return out

    if provider_name == "open-meteo":
        return _get_openmeteo_data(filters)

    raise DataIngestionError(f"Unsupported weather provider: {provider_name}")


def _get_openmeteo_data(filters: dict[str, Any]) -> pd.DataFrame:
    """Fetch weather data from Open-Meteo for the given filters."""
    provider = OpenMeteoProvider()
    location_id, lat, lon = _resolve_location(filters)

    # If no lat/lon available, attempt geocoding.
    if lat is None or lon is None:
        state = filters.get("state")
        district = filters.get("district")
        if state and district:
            try:
                lat, lon = provider.geocode(str(state), str(district))
            except DataIngestionError as exc:
                logger.warning(
                    "Open-Meteo geocoding failed: %s. Falling back to CSV.", exc
                )
                df = get_filtered(filters)
                weather_cols = [
                    c
                    for c in df.columns
                    if c in ("rainfall", "temperature", "humidity", "soil_moisture")
                ]
                if not weather_cols:
                    return pd.DataFrame()
                out = df[weather_cols].copy()
                out["timestamp"] = df.get("date", pd.NaT)
                out["location_id"] = location_id
                out["source"] = "csv"
                return out
        else:
            logger.warning(
                "Open-Meteo requires state and district for geocoding. Falling back to CSV."
            )
            df = get_filtered(filters)
            weather_cols = [
                c
                for c in df.columns
                if c in ("rainfall", "temperature", "humidity", "soil_moisture")
            ]
            if not weather_cols:
                return pd.DataFrame()
            out = df[weather_cols].copy()
            out["timestamp"] = df.get("date", pd.NaT)
            out["location_id"] = location_id
            out["source"] = "csv"
            return out

    start_date = filters.get("start_date") or "2022-01-01"
    end_date = filters.get("end_date") or "2024-12-31"

    try:
        records = provider.fetch_historical(location_id, lat, lon, start_date, end_date)
        if not records:
            logger.warning(
                "Open-Meteo returned no records for %s (%s to %s)",
                location_id,
                start_date,
                end_date,
            )
            return pd.DataFrame()
        df = pd.DataFrame([r.model_dump() for r in records])
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["date"] = df["timestamp"].dt.date
        return df
    except DataIngestionError as exc:
        logger.warning("Open-Meteo fetch failed: %s. Falling back to CSV.", exc)
        df = get_filtered(filters)
        weather_cols = [
            c
            for c in df.columns
            if c in ("rainfall", "temperature", "humidity", "soil_moisture")
        ]
        if not weather_cols:
            return pd.DataFrame()
        out = df[weather_cols].copy()
        out["timestamp"] = df.get("date", pd.NaT)
        out["location_id"] = location_id
        out["source"] = "csv"
        return out


def get_weather_source() -> str:
    """Return the active weather data source name."""
    return get_data_ingestion_settings().provider


def get_filtered(filters: dict[str, Any] | None = None) -> pd.DataFrame:
    """Apply dashboard filters to the dataset and return the subset."""
    df = get_dataset().copy()
    filters = filters or {}

    if "crop" in filters and filters["crop"] and "crop" in df.columns:
        df = df[df["crop"].astype(str) == str(filters["crop"])]
    if "state" in filters and filters["state"] and "state" in df.columns:
        df = df[df["state"].astype(str) == str(filters["state"])]
    if "district" in filters and filters["district"] and "district" in df.columns:
        df = df[df["district"].astype(str) == str(filters["district"])]
    if "date" in df.columns:
        if filters.get("start_date"):
            df = df[df["date"] >= pd.to_datetime(filters["start_date"])]
        if filters.get("end_date"):
            df = df[df["date"] <= pd.to_datetime(filters["end_date"])]
    return df


def get_filter_options() -> dict[str, list[str] | float | str | bool]:
    """Return distinct values for the filter dropdowns."""
    df = get_dataset()
    options: dict[str, list[str] | float | str | bool] = {}
    for col in ("crop", "state", "district"):
        if col in df.columns:
            options[col] = df[col].dropna().astype(str).unique().tolist()
    if "date" in df.columns:
        options["date_min"] = df["date"].min()
        options["date_max"] = df["date"].max()
    options["loaded"] = len(df) > 0
    options["weather_source"] = get_weather_source()
    return options
