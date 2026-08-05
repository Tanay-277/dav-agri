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


# --- Insights / Story / Recommendations ---
class Insight(BaseModel):
    type: str = Field(..., description="e.g. trend, anomaly, comparison")
    metric: str | None = None
    message: str
    severity: str = Field("info", description="info | warning | critical")
    magnitude: float | None = None


class Recommendation(BaseModel):
    condition: str
    message: str
    priority: str = Field("medium", description="low | medium | high")
    action: str | None = None


class Story(BaseModel):
    story: str
    summary: str
    reasons: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    source: str = Field("rule", description="rule | ai")


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
