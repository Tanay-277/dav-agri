from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class IntentCategory(str, Enum):
    CURRENT_CONDITIONS = "current_conditions"
    FORECAST = "forecast"
    TEMPERATURE_QUERY = "temperature_query"
    RAINFALL_QUERY = "rainfall_query"
    WIND_QUERY = "wind_query"
    HUMIDITY_QUERY = "humidity_query"
    SOIL_QUERY = "soil_query"
    YIELD_QUERY = "yield_query"
    COMPARISON = "comparison"
    TREND_QUERY = "trend_query"
    HISTORICAL_QUERY = "historical_query"
    RECOMMENDATION_QUERY = "recommendation_query"
    THRESHOLD_QUERY = "threshold_query"
    ANOMALY_QUERY = "anomaly_query"
    GENERAL_QUERY = "general_query"
    FILTER = "filter"
    HELP = "help"
    RESET = "reset"
    READ_ALOUD = "read_aloud"
    STOP = "stop"
    PAUSE = "pause"
    RESUME = "resume"
    UNSUPPORTED = "unsupported"


class TimePeriod(BaseModel):
    start: str | None = None
    end: str | None = None
    relative: str | None = Field(default=None, description="e.g. 'tomorrow', 'yesterday', 'next_week'")
    is_historical: bool = False
    is_future: bool = False


class ComparisonSpec(BaseModel):
    type: str = Field(default="time", description="time | location | metric")
    entities: list[str] = Field(default_factory=list)
    metric: str | None = None


class StructuredQuery(BaseModel):
    intent: IntentCategory = Field(..., description="Classified user intent")
    entities: dict[str, Any] = Field(
        default_factory=dict,
        description="Extracted entities: crop, state, district, metric, etc.",
    )
    time_period: TimePeriod = Field(default_factory=TimePeriod)
    variables: list[str] = Field(
        default_factory=list, description="Canonical metric names to analyze"
    )
    comparison: ComparisonSpec | None = None
    aggregation: str | None = Field(default=None, description="daily | weekly | monthly")
    units: str | None = Field(default=None, description="Preferred output units")
    language: str | None = Field(default=None, description="Detected language code")
    output_type: str = Field(default="summary", description="summary | detailed | chart | recommendation")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Parsing confidence 0-1")
    needs_clarification: bool = Field(default=False)
    clarification_options: list[str] = Field(default_factory=list)
    raw_query: str = Field(..., description="Original user query text")
    ambiguity_reasons: list[str] = Field(default_factory=list)
    unsupported_reason: str | None = Field(default=None)

    model_config = {"use_enum_values": True}
