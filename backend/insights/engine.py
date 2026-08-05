from __future__ import annotations

from typing import Any

import pandas as pd

from core.config import get_settings
from core.logging import get_logger
from insights.gemini import GeminiClient
from models.schemas import Insight

logger = get_logger(__name__)


def _avg(df: pd.DataFrame, col: str) -> float | None:
    if col not in df.columns or df[col].dropna().empty:
        return None
    return float(df[col].mean())


def _last_two_periods(
    df: pd.DataFrame, col: str, period: str = "M"
) -> tuple[float | None, float | None]:
    """Return (previous, current) mean for a metric grouped by date period."""
    if col not in df.columns or "date" not in df.columns:
        return None, None
    sub = df[["date", col]].dropna()
    if sub.empty:
        return None, None
    sub = sub.copy()
    sub["_p"] = sub["date"].dt.to_period(period).astype(str)
    groups = sub.groupby("_p")[col].mean().sort_index()
    if len(groups) < 2:
        return None, None
    return float(groups.iloc[-2]), float(groups.iloc[-1])


def _metric_label(metric: str) -> str:
    return metric.replace("_", " ").title()


def _change_insight(prev: float, curr: float, metric: str) -> Insight | None:
    if prev is None or curr is None or prev == 0:
        return None
    delta = (curr - prev) / prev * 100
    direction = "increased" if delta > 0 else "decreased"
    severity = "info" if abs(delta) < 10 else ("warning" if abs(delta) < 25 else "critical")
    return Insight(
        type="trend",
        metric=metric,
        message=(
            f"{_metric_label(metric)} {direction} by {abs(delta):.1f}% compared to the "
            "previous period."
        ),
        severity=severity,
        magnitude=round(delta, 1),
    )


def _threshold_insights(df: pd.DataFrame) -> list[Insight]:
    """Compare overall averages to year-to-date / anomaly thresholds."""
    out: list[Insight] = []

    # Yield vs overall average
    overall = df.get("overall_yield")  # not present; placeholder removed
    del overall

    yield_col = "yield" if "yield" in df.columns else None
    if yield_col is not None:
        vals = df[yield_col].dropna()
        if not vals.empty:
            avg = float(vals.mean())
            latest = float(vals.iloc[-1]) if len(vals) else avg
            if avg != 0:
                diff = (latest - avg) / avg * 100
                out.append(
                    Insight(
                        type="comparison",
                        metric="yield",
                        message=(
                            f"Yield is {abs(diff):.1f}% {'above' if diff > 0 else 'below'} "
                            "the average for the selected period."
                        ),
                        severity="info" if abs(diff) < 10 else "warning",
                        magnitude=round(diff, 1),
                    )
                )

    # Rainfall anomaly
    rain = "rainfall" if "rainfall" in df.columns else None
    if rain is not None:
        vals = df[rain].dropna()
        if not vals.empty and vals.mean() > 0:
            latest = float(vals.iloc[-1])
            avg = float(vals.mean())
            if avg > 0:
                ratio = (latest - avg) / avg * 100
                if abs(ratio) >= 20:
                    out.append(
                        Insight(
                            type="anomaly",
                            metric="rainfall",
                            message=(
                                f"Latest rainfall is {ratio:+.1f}% vs the period "
                                "average — a notable deviation."
                            ),
                            severity="warning",
                            magnitude=round(ratio, 1),
                        )
                    )
    return out


def generate_insights(df: pd.DataFrame) -> list[Insight]:
    """Rule-based insight detection. Falls back gracefully on empty data."""
    if df.empty:
        return [
            Insight(
                type="info",
                metric=None,
                message="No data available for the selected filters.",
                severity="info",
            )
        ]

    insights: list[Insight] = []

    for metric in ("rainfall", "temperature", "soil_moisture"):
        prev, curr = _last_two_periods(df, metric)
        change = _change_insight(prev, curr, metric)
        if change:
            insights.append(change)

    insights.extend(_threshold_insights(df))
    return insights


def generate_story(
    df: pd.DataFrame, insights: list[Insight], recommendations: list[dict]
) -> dict[str, Any]:
    """Combine insights + recommendations into a narrative. Uses Gemini if enabled."""
    settings = get_settings()

    summary = _build_summary(df, insights)
    reasons = _build_reasons(insights)
    recs = [r["message"] for r in recommendations]

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


def _build_summary(df: pd.DataFrame, insights: list[Insight]) -> str:
    if df.empty:
        return "No data is available for the selected filters."
    parts = []
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
        if i.metric in ("rainfall", "temperature", "soil_moisture"):
            reasons.append(f"Changes in {i.metric} influence overall crop conditions.")
    return reasons or ["Historical patterns indicate environmental drivers."]


def _compose_rule_story(summary: str, reasons: list[str], recs: list[str]) -> str:
    story = summary
    if reasons:
        story += " " + " ".join(reasons)
    if recs:
        story += " Recommended actions: " + " ".join(recs)
    return story
