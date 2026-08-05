from __future__ import annotations

from functools import lru_cache
from typing import Any

import pandas as pd

from core.config import get_settings
from core.logging import get_logger
from database.db import set_meta

logger = get_logger(__name__)

# Normalised column names -> list of accepted raw headers (lowercased).
COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
    "crop": ("crop", "crop_type", "cropname"),
    "state": ("state", "state_name", "region"),
    "district": ("district", "district_name", "area"),
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


def get_filter_options() -> dict[str, list[str]]:
    """Return distinct values for the filter dropdowns."""
    df = get_dataset()
    options: dict[str, list[str]] = {}
    for col in ("crop", "state", "district"):
        if col in df.columns:
            options[col] = (
                df[col].dropna().astype(str).unique().tolist()
            )
    if "date" in df.columns:
        options["date_min"] = df["date"].min()
        options["date_max"] = df["date"].max()
    options["loaded"] = len(df) > 0
    return options
