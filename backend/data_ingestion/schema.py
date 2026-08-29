from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field


class RawAgriculturalRecord(BaseModel):
    """Schema for raw CSV rows before normalization."""

    record_date: str | None = Field(
        default=None, description="Raw date string from CSV"
    )
    state: str | None = Field(default=None)
    district: str | None = Field(default=None)
    crop: str | None = Field(default=None)
    rainfall: float | str | None = Field(default=None, description="Raw rainfall value")
    temperature: float | str | None = Field(default=None)
    humidity: float | str | None = Field(default=None)
    soil_moisture: float | str | None = Field(default=None)
    yield_kg: float | str | None = Field(default=None, alias="yield")
    production_tonnes: float | str | None = Field(default=None, alias="production")
    area_ha: float | str | None = Field(default=None, alias="area")
    fertilizer_kg: float | str | None = Field(default=None, alias="fertilizer")
    irrigation_pct: float | str | None = Field(default=None, alias="irrigation")

    model_config = {"populate_by_name": True}


class NormalizedAgriculturalRecord(BaseModel):
    """Canonical internal schema for agricultural/weather data."""

    timestamp: datetime = Field(..., description="UTC datetime of the observation")
    record_date: date = Field(..., description="Date part of the observation")
    state: str = Field(..., description="Normalized state name")
    district: str = Field(..., description="Normalized district name")
    crop: str = Field(..., description="Normalized crop name")
    rainfall_mm: float | None = Field(
        default=None, description="Rainfall in millimeters"
    )
    temperature_c: float | None = Field(
        default=None, description="Temperature in degrees Celsius"
    )
    humidity_pct: float | None = Field(
        default=None, description="Relative humidity percentage [0-100]"
    )
    soil_moisture_pct: float | None = Field(
        default=None, description="Soil moisture percentage [0-100]"
    )
    yield_kg_per_ha: float | None = Field(
        default=None, description="Yield in kg per hectare"
    )
    production_tonnes: float | None = Field(
        default=None, description="Production in metric tonnes"
    )
    area_ha: float | None = Field(default=None, description="Cropped area in hectares")
    fertilizer_kg: float | None = Field(
        default=None, description="Fertilizer usage in kg"
    )
    irrigation_pct: float | None = Field(
        default=None, description="Irrigation percentage [0-100]"
    )
    location_id: str = Field(..., description="Normalized location identifier")
    latitude: float | None = Field(
        default=None, description="Decimal degrees, positive=N"
    )
    longitude: float | None = Field(
        default=None, description="Decimal degrees, positive=E"
    )
    data_classification: str = Field(
        default="historical",
        description="Data temporal classification: historical | current | forecast",
    )
    source: str = Field(..., description="Data source identifier")
    source_row_id: int | None = Field(
        default=None, description="Original row index or ID"
    )
    is_duplicate: bool = Field(
        default=False, description="True if this row is a detected duplicate"
    )
    is_outlier: bool = Field(
        default=False, description="True if any field is flagged as outlier"
    )
    is_invalid: bool = Field(
        default=False, description="True if any field fails validation"
    )
    validation_flags: list[str] = Field(
        default_factory=list, description="List of validation/quality flags"
    )
    raw: dict[str, Any] | None = Field(
        default=None, description="Original raw values for traceability"
    )

    model_config = {"use_enum_values": True}


class ValidationRule(BaseModel):
    """Single validation rule for a field."""

    field: str
    rule_type: str = Field(
        ...,
        description="range | null | duplicate | outlier | type | categorical",
    )
    min_value: float | None = Field(default=None)
    max_value: float | None = Field(default=None)
    allowed_values: list[str] | None = Field(default=None)
    message: str = Field(default="Validation failed")
