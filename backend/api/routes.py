from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response

from analytics import charts, engine as kpi_engine
from core.config import get_settings, Settings
from core.logging import get_logger
from database import data
from database.db import record_insight_run
from insights import engine as insight_engine
from models.schemas import (
    DashboardFilters,
    DashboardResponse,
    InsightsResponse,
    KPI,
    RecommendationsResponse,
    Story,
)
from recommendations import engine as rec_engine

logger = get_logger(__name__)
router = APIRouter()


def _as_filter_dict(filters: DashboardFilters) -> dict:
    return filters.model_dump(exclude_none=True)


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "app": get_settings().APP_NAME}


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    filters: DashboardFilters = Depends(),
) -> DashboardResponse:
    df = data.get_filtered(_as_filter_dict(filters))

    kpis: list[KPI] = kpi_engine.compute_kpis(df)
    charts_data = {
        "line": charts.line_chart(df),
        "bar": charts.bar_chart(df),
        "scatter": charts.scatter_chart(df),
        "heatmap": charts.heatmap_data(df),
        "pie": charts.pie_chart(df),
    }
    return DashboardResponse(
        charts=charts_data,
        kpis=kpis,
        filters=data.get_filter_options(),
        metadata={"rows": int(len(df))},
    )


@router.get("/insights", response_model=InsightsResponse)
def get_insights(
    filters: DashboardFilters = Depends(),
) -> InsightsResponse:
    df = data.get_filtered(_as_filter_dict(filters))
    insights = insight_engine.generate_insights(df)
    record_insight_run(_as_filter_dict(filters), [i.model_dump() for i in insights])
    return InsightsResponse(insights=insights)


@router.get("/story", response_model=Story)
def get_story(
    filters: DashboardFilters = Depends(),
) -> Story:
    df = data.get_filtered(_as_filter_dict(filters))
    insights = insight_engine.generate_insights(df)
    recs = rec_engine.generate_recommendations(df)
    result = insight_engine.generate_story(df, insights, [r.model_dump() for r in recs])
    record_insight_run(_as_filter_dict(filters), [i.model_dump() for i in insights], result["story"])
    return Story(**result)


@router.get("/recommendations", response_model=RecommendationsResponse)
def get_recommendations(
    filters: DashboardFilters = Depends(),
) -> RecommendationsResponse:
    df = data.get_filtered(_as_filter_dict(filters))
    return RecommendationsResponse(recommendations=rec_engine.generate_recommendations(df))


@router.get("/filters")
def get_filters() -> dict:
    return data.get_filter_options()


@router.post("/export")
def export_dashboard(
    filters: DashboardFilters = None,
    format: str = Query("pdf", pattern="^(pdf|json)$"),
) -> Response:
    """Export the dashboard as PDF (or JSON fallback)."""
    from api.export import export_dashboard as build_export

    return build_export(filters, format)


@router.get("/dataset/status")
def dataset_status() -> dict:
    df = data.get_dataset()
    return {
        "loaded": not df.empty,
        "rows": int(len(df)),
        "columns": list(df.columns),
    }
