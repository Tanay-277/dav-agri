from __future__ import annotations

from typing import Any

import pandas as pd

from analytics.engine import _mean as _avg
from analytics.engine import generate_insights
from core.config import get_settings
from core.logging import get_logger
from insights.gemini import GeminiClient
from models.schemas import Insight

logger = get_logger(__name__)

__all__ = ["generate_story", "generate_insights"]


def _metric_label(metric: str | None) -> str:
    if not metric:
        return "metric"
    return metric.replace("_", " ").title()


def _build_summary(df: pd.DataFrame, insights: list[Insight]) -> str:
    if df.empty:
        return "No data is available for the selected filters."
    parts: list[str] = []
    rain = _avg(df, "rainfall")
    temp = _avg(df, "temperature")
    yield_ = _avg(df, "yield")
    if rain is not None:
        parts.append(f"average rainfall of {rain:.1f}mm")
    if temp is not None:
        parts.append(f"average temperature of {temp:.1f}°C")
    if yield_ is not None:
        parts.append(f"average yield of {yield_:.1f} units")
    base = "For the selected period, the dataset shows " + ", ".join(parts) + "."
    trends = [i.message for i in insights if i.type == "trend"]
    if trends:
        base += " " + " ".join(trends)
    return base


def _build_reasons(insights: list[Insight]) -> list[str]:
    reasons: list[str] = []
    for i in insights:
        if i.metric and i.metric in (
            "rainfall",
            "temperature",
            "soil_moisture",
            "humidity",
        ):
            reasons.append(
                f"Changes in {i.metric.replace('_', ' ')} influence overall crop conditions."
            )
    return reasons or ["Historical patterns indicate environmental drivers."]


def _compose_rule_story(summary: str, reasons: list[str], recs: list[str]) -> str:
    story = summary
    if reasons:
        story += " " + " ".join(reasons)
    if recs:
        story += " Recommended actions: " + " ".join(recs)
    return story


def generate_story(
    df: pd.DataFrame, insights: list[Insight], recommendations: list[dict]
) -> dict[str, Any]:
    """Combine insights + recommendations into a narrative. Uses Gemini if enabled."""
    settings = get_settings()

    summary = _build_summary(df, insights)
    reasons = _build_reasons(insights)
    recs = [r.get("message", "") for r in recommendations if r.get("message")]

    source = "rule"
    if settings.AI_ENABLED and settings.GEMINI_API_KEY:
        try:
            gemini = GeminiClient(settings.GEMINI_API_KEY, settings.GEMINI_MODEL)
            story_text = gemini.generate_story(summary, reasons, recs)
            source = "ai"
        except Exception as exc:  # pragma: no cover
            logger.warning("Gemini story generation failed: %s", exc)
            story_text = _compose_rule_story(summary, reasons, recs)
    else:
        story_text = _compose_rule_story(summary, reasons, recs)

    return {
        "story": story_text,
        "summary": summary,
        "reasons": reasons,
        "recommendations": recs,
        "source": source,
    }
