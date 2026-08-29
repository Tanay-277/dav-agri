from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


# --- Filters ---
class DashboardFilters(BaseModel):
    crop: str | None = None
    state: str | None = None
    district: str | None = None
    start_date: str | None = None
    end_date: str | None = None


# --- KPI ---
class KPI(BaseModel):
    label: str
    value: float | int | str | None
    unit: str | None = None
    change: float | None = None
    change_label: str | None = None


# --- Analytics / Insight ---
class Insight(BaseModel):
    type: str = Field(
        ...,
        description="Insight category: trend | anomaly | comparison | threshold | forecast | current_conditions",
    )
    metric: str | None = Field(
        default=None, description="Primary metric, e.g. 'rainfall_mm'"
    )
    message: str = Field(..., description="Human-readable explanation")
    severity: str = Field(default="info", description="info | warning | critical")
    magnitude: float | None = Field(
        default=None, description="Numeric magnitude of the effect"
    )
    input_variables: dict[str, Any] = Field(
        default_factory=dict, description="Variables used to compute the insight"
    )
    time_range: dict[str, str | None] = Field(
        default_factory=dict, description="Start and end timestamps used"
    )
    calculation_method: str = Field(
        default="", description="Deterministic method used to derive the insight"
    )
    result: dict[str, Any] = Field(
        default_factory=dict, description="Structured numeric result"
    )
    confidence: float | None = Field(
        default=None, description="Confidence score 0-1 (None = not applicable)"
    )
    source: str = Field(default="rule", description="rule | ai")
    data_quality_flags: list[str] = Field(
        default_factory=list, description="Quality issues affecting this insight"
    )

    model_config = {"use_enum_values": True}


class Recommendation(BaseModel):
    condition: str
    message: str
    priority: str = Field(default="medium", description="low | medium | high")
    action: str | None = None


class Story(BaseModel):
    story: str
    summary: str
    reasons: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    source: str = Field(default="rule", description="rule | ai")


# --- Dashboard payloads ---
class DashboardResponse(BaseModel):
    charts: dict[str, Any]
    kpis: list[KPI]
    filters: dict[str, Any]
    metadata: dict[str, Any]


class InsightsResponse(BaseModel):
    insights: list[Insight]


class RecommendationsResponse(BaseModel):
    recommendations: list[Recommendation]


# --- Research / MVRS ---
class TaskLog(BaseModel):
    task_id: str
    condition: str
    user_id: str | None = None
    completed: bool = False
    duration_ms: int | None = None
    voice_used: bool = False
    error: str | None = None


class SurveyResponse(BaseModel):
    task_id: str | None = None
    condition: str
    user_id: str | None = None
    comprehension_score: int | None = None
    trust_score: int | None = None
    sus_score: int | None = None
    feedback: str | None = None


class ResearchCondition(BaseModel):
    condition: str = Field(
        ..., description="conventional | voice-only | voice-icons | voice-story"
    )


class ErrorLog(BaseModel):
    message: str
    component_stack: str | None = None
    url: str | None = None
    user_agent: str | None = None
