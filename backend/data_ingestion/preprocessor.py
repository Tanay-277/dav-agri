from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd

from core.logging import get_logger
from data_ingestion.locations import (
    build_location_id,
    get_centroid,
    normalize_district,
    normalize_state,
)
from data_ingestion.schema import (
    NormalizedAgriculturalRecord,
    ValidationRule,
)

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Validation rules
# ---------------------------------------------------------------------------
_NUMERIC_RULES: list[ValidationRule] = [
    ValidationRule(
        field="rainfall_mm",
        rule_type="range",
        min_value=0,
        max_value=500,
        message="Rainfall must be 0–500 mm",
    ),
    ValidationRule(
        field="temperature_c",
        rule_type="range",
        min_value=-10,
        max_value=60,
        message="Temperature must be -10–60 °C",
    ),
    ValidationRule(
        field="humidity_pct",
        rule_type="range",
        min_value=0,
        max_value=100,
        message="Humidity must be 0–100 %",
    ),
    ValidationRule(
        field="soil_moisture_pct",
        rule_type="range",
        min_value=0,
        max_value=100,
        message="Soil moisture must be 0–100 %",
    ),
    ValidationRule(
        field="yield_kg_per_ha",
        rule_type="range",
        min_value=0,
        max_value=10000,
        message="Yield must be 0–10,000 kg/ha",
    ),
    ValidationRule(
        field="production_tonnes",
        rule_type="range",
        min_value=0,
        max_value=50000,
        message="Production must be 0–50,000 t",
    ),
    ValidationRule(
        field="area_ha",
        rule_type="range",
        min_value=0,
        max_value=100000,
        message="Area must be 0–100,000 ha",
    ),
    ValidationRule(
        field="fertilizer_kg",
        rule_type="range",
        min_value=0,
        max_value=50000,
        message="Fertilizer must be 0–50,000 kg",
    ),
    ValidationRule(
        field="irrigation_pct",
        rule_type="range",
        min_value=0,
        max_value=100,
        message="Irrigation must be 0–100 %",
    ),
]

_CATEGORICAL_RULES: list[ValidationRule] = [
    ValidationRule(
        field="state",
        rule_type="categorical",
        allowed_values=[
            "Andhra Pradesh",
            "Gujarat",
            "Karnataka",
            "Madhya Pradesh",
            "Maharashtra",
            "Punjab",
            "Rajasthan",
            "Tamil Nadu",
        ],
        message="State not in controlled vocabulary",
    ),
    ValidationRule(
        field="crop",
        rule_type="categorical",
        allowed_values=[
            "Cotton",
            "Groundnut",
            "Maize",
            "Pulses",
            "Rice",
            "Soybean",
            "Sugarcane",
            "Wheat",
        ],
        message="Crop not in controlled vocabulary",
    ),
]


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------
class DataPreprocessor:
    """Transform raw agricultural CSV data into a normalized, validated DataFrame."""

    def __init__(self, source_name: str = "agriculture.csv") -> None:
        self.source_name = source_name
        self.quality_log: list[str] = []
        self.validation_errors: list[str] = []

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            logger.warning("Empty DataFrame provided to preprocessor")
            return df

        self.quality_log.append(f"Input rows: {len(df)}")
        df = self._normalize_column_names(df)
        df = self._normalize_types(df)
        df = self._normalize_locations(df)
        df = self._normalize_timestamps(df)
        df = self._detect_duplicates(df)
        df = self._detect_invalid_values(df)
        df = self._detect_outliers(df)
        df = self._classify_data(df)
        df = self._track_source(df)
        self.quality_log.append(f"Output rows: {len(df)}")
        return df

    def to_normalized_records(
        self, df: pd.DataFrame
    ) -> list[NormalizedAgriculturalRecord]:
        records: list[NormalizedAgriculturalRecord] = []
        for idx, row in df.iterrows():
            raw_dict = {k: (None if _is_null(v) else v) for k, v in row.items()}
            try:
                rec = NormalizedAgriculturalRecord(
                    timestamp=row["timestamp"],
                    record_date=(
                        row["record_date"].date()
                        if hasattr(row["record_date"], "date")
                        else row["record_date"]
                    ),
                    state=str(row.get("state", "")),
                    district=str(row.get("district", "")),
                    crop=str(row.get("crop", "")),
                    rainfall_mm=_safe_float(row.get("rainfall_mm")),
                    temperature_c=_safe_float(row.get("temperature_c")),
                    humidity_pct=_safe_float(row.get("humidity_pct")),
                    soil_moisture_pct=_safe_float(row.get("soil_moisture_pct")),
                    yield_kg_per_ha=_safe_float(row.get("yield_kg_per_ha")),
                    production_tonnes=_safe_float(row.get("production_tonnes")),
                    area_ha=_safe_float(row.get("area_ha")),
                    fertilizer_kg=_safe_float(row.get("fertilizer_kg")),
                    irrigation_pct=_safe_float(row.get("irrigation_pct")),
                    location_id=str(row.get("location_id", "")),
                    latitude=_safe_float(row.get("latitude")),
                    longitude=_safe_float(row.get("longitude")),
                    data_classification=str(
                        row.get("data_classification", "historical")
                    ),
                    source=str(row.get("source", self.source_name)),
                    source_row_id=_safe_int(idx),
                    is_duplicate=bool(row.get("is_duplicate", False)),
                    is_outlier=bool(row.get("is_outlier", False)),
                    is_invalid=bool(row.get("is_invalid", False)),
                    validation_flags=list(row.get("validation_flags", [])),
                    raw=raw_dict,
                )
                records.append(rec)
            except Exception as exc:
                logger.warning("Failed to normalize row %s: %s", idx, exc)
                self.validation_errors.append(f"Row {idx}: {exc}")
        return records

    def _normalize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        from database.data import _normalise_columns

        df = _normalise_columns(df)
        rename_map = {
            "date": "record_date",
            "rainfall": "rainfall_mm",
            "temperature": "temperature_c",
            "humidity": "humidity_pct",
            "soil_moisture": "soil_moisture_pct",
            "yield": "yield_kg_per_ha",
            "production": "production_tonnes",
            "area": "area_ha",
            "fertilizer": "fertilizer_kg",
            "irrigation": "irrigation_pct",
        }
        df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
        self.quality_log.append(f"Columns after normalization: {list(df.columns)}")
        return df

    def _normalize_types(self, df: pd.DataFrame) -> pd.DataFrame:
        numeric_cols = [
            "rainfall_mm",
            "temperature_c",
            "humidity_pct",
            "soil_moisture_pct",
            "yield_kg_per_ha",
            "production_tonnes",
            "area_ha",
            "fertilizer_kg",
            "irrigation_pct",
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        for col in ("state", "district", "crop"):
            if col in df.columns:
                df[col] = df[col].astype(str).replace("nan", "")
        return df

    def _normalize_locations(self, df: pd.DataFrame) -> pd.DataFrame:
        if "state" in df.columns:
            df["state"] = df["state"].apply(normalize_state)
        if "district" in df.columns:
            df["district"] = df["district"].apply(
                lambda x: normalize_district(
                    x, df["state"].iloc[0] if len(df) else None
                )
            )
        df["location_id"] = df.apply(
            lambda r: build_location_id(r.get("state"), r.get("district")), axis=1
        )
        df["latitude"] = df["location_id"].apply(
            lambda lid: get_centroid(lid)[0] if get_centroid(lid) else None
        )
        df["longitude"] = df["location_id"].apply(
            lambda lid: get_centroid(lid)[1] if get_centroid(lid) else None
        )
        return df

    def _normalize_timestamps(self, df: pd.DataFrame) -> pd.DataFrame:
        if "record_date" in df.columns:
            df["record_date"] = pd.to_datetime(df["record_date"], errors="coerce")
            df["timestamp"] = pd.to_datetime(df["record_date"], errors="coerce")
        else:
            df["timestamp"] = pd.NaT
            df["record_date"] = pd.NaT
        return df

    def _detect_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        subset = [
            c for c in ("record_date", "state", "district", "crop") if c in df.columns
        ]
        if not subset:
            return df
        dup_mask = df.duplicated(subset=subset, keep="first")
        df["is_duplicate"] = dup_mask
        n_dups = int(dup_mask.sum())
        if n_dups:
            self.quality_log.append(f"Duplicates detected: {n_dups}")
        return df

    def _detect_invalid_values(self, df: pd.DataFrame) -> pd.DataFrame:
        flags: list[list[str]] = [[] for _ in range(len(df))]
        for rule in _NUMERIC_RULES:
            col = rule.field
            if col not in df.columns:
                continue
            series = pd.to_numeric(df[col], errors="coerce")
            if rule.min_value is not None:
                mask = series < rule.min_value
                for i in mask[mask].index:
                    flags[i].append(f"{col}: {rule.message} (< {rule.min_value})")
            if rule.max_value is not None:
                mask = series > rule.max_value
                for i in mask[mask].index:
                    flags[i].append(f"{col}: {rule.message} (> {rule.max_value})")
        for rule in _CATEGORICAL_RULES:
            col = rule.field
            if col not in df.columns or rule.allowed_values is None:
                continue
            mask = ~df[col].isin(rule.allowed_values)
            for i in mask[mask].index:
                flags[i].append(f"{col}: {rule.message} (value={df.at[i, col]!r})")
        df["validation_flags"] = [list(set(f)) for f in flags]
        df["is_invalid"] = [bool(f) for f in df["validation_flags"]]
        invalid_count = int(df["is_invalid"].sum())
        if invalid_count:
            self.quality_log.append(f"Invalid values detected: {invalid_count} rows")
        return df

    def _detect_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        outlier_cols = [
            "rainfall_mm",
            "temperature_c",
            "humidity_pct",
            "soil_moisture_pct",
            "yield_kg_per_ha",
            "production_tonnes",
            "area_ha",
            "fertilizer_kg",
            "irrigation_pct",
        ]
        outlier_flags: list[list[str]] = [[] for _ in range(len(df))]
        for col in outlier_cols:
            if col not in df.columns:
                continue
            s = pd.to_numeric(df[col], errors="coerce").dropna()
            if s.empty:
                continue
            q1, q3 = s.quantile([0.25, 0.75])
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            mask = (df[col] < lower) | (df[col] > upper)
            for i in mask[mask].index:
                outlier_flags[i].append(f"{col}: IQR outlier ({df.at[i, col]})")
        for i, flags in enumerate(outlier_flags):
            if flags:
                existing = set(
                    df.at[i, "validation_flags"]
                    if "validation_flags" in df.columns
                    else []
                )
                existing.update(flags)
                df.at[i, "validation_flags"] = list(existing)
        df["is_outlier"] = [bool(f) for f in df["validation_flags"]]
        outlier_count = int(df["is_outlier"].sum())
        if outlier_count:
            self.quality_log.append(f"Outliers detected: {outlier_count} rows")
        return df

    def _classify_data(self, df: pd.DataFrame) -> pd.DataFrame:
        today = datetime.utcnow().date()
        if "record_date" in df.columns:
            df["data_classification"] = df["record_date"].apply(
                lambda d: (
                    "future"
                    if pd.notna(d) and d.date() > today
                    else "historical" if hasattr(d, "date") else "historical"
                )
            )
        else:
            df["data_classification"] = "historical"
        return df

    def _track_source(self, df: pd.DataFrame) -> pd.DataFrame:
        df["source"] = self.source_name
        if pd.api.types.is_integer_dtype(df.index):
            df["source_row_id"] = df.index
        else:
            df["source_row_id"] = range(len(df))
        return df


def _safe_float(value: Any) -> float | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    try:
        f = float(value)
        return None if pd.isna(f) else f
    except (TypeError, ValueError):
        return None


def _safe_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _is_null(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and pd.isna(value):
        return True
    try:
        result = pd.isna(value)
        if hasattr(result, "size") and result.size > 1:
            return False
        return bool(result)
    except (TypeError, ValueError):
        return False
