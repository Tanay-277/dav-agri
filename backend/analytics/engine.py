from __future__ import annotations

from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd

from models.schemas import KPI, Insight


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """Return the first matching column name present in the DataFrame."""
    for name in candidates:
        if name in df.columns:
            return name
    return None


def _safe_float(value: Any) -> float | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return None


def _make_insight(
    type: str,
    metric: str | None,
    message: str,
    severity: str = "info",
    magnitude: float | None = None,
    input_variables: dict[str, Any] | None = None,
    time_range: dict[str, str | None] | None = None,
    calculation_method: str = "",
    result: dict[str, Any] | None = None,
    confidence: float | None = None,
    source: str = "rule",
    data_quality_flags: list[str] | None = None,
) -> Insight:
    return Insight(
        type=type,
        metric=metric,
        message=message,
        severity=severity,
        magnitude=magnitude,
        input_variables=input_variables or {},
        time_range=time_range or {},
        calculation_method=calculation_method,
        result=result or {},
        confidence=confidence,
        source=source,
        data_quality_flags=data_quality_flags or [],
    )


def _get_time_bounds(df: pd.DataFrame) -> tuple[str | None, str | None]:
    date_col = _col(df, ["record_date", "date"])
    if date_col is None or df[date_col].dropna().empty:
        return None, None
    start = df[date_col].min()
    end = df[date_col].max()
    if hasattr(start, "strftime"):
        start = start.strftime("%Y-%m-%d")
    if hasattr(end, "strftime"):
        end = end.strftime("%Y-%m-%d")
    return start, end


def _mean(df: pd.DataFrame, col: str) -> float | None:
    if col not in df.columns or df[col].dropna().empty:
        return None
    return round(float(df[col].mean()), 2)


def _pct_change(df: pd.DataFrame, col: str, order_by: str = "date") -> float | None:
    """Percentage change between first and last group for a metric."""
    if col not in df.columns or order_by not in df.columns:
        return None
    s = df[[order_by, col]].dropna()
    if s.empty:
        return None
    s = s.sort_values(order_by)
    first, last = s[col].iloc[0], s[col].iloc[-1]
    if first == 0:
        return None
    return round(float((last - first) / first) * 100, 1)


# ---------------------------------------------------------------------------
# KPIs
# ---------------------------------------------------------------------------
def compute_kpis(df: pd.DataFrame) -> list[KPI]:
    if df.empty:
        return [
            KPI(label="Avg Rainfall", value="—", unit="mm"),
            KPI(label="Avg Temperature", value="—", unit="°C"),
            KPI(label="Highest Yield", value="—", unit="kg"),
            KPI(label="Lowest Yield", value="—", unit="kg"),
            KPI(label="Total Production", value="—", unit="t"),
            KPI(label="Avg Soil Moisture", value="—", unit="%"),
        ]

    kpis: list[KPI] = []

    def add(label: str, value: Any, unit: str, col: str, kind: str = "mean") -> None:
        if col not in df.columns:
            kpis.append(KPI(label=label, value="—", unit=unit))
            return
        col_s = df[col].dropna()
        if col_s.empty:
            kpis.append(KPI(label=label, value="—", unit=unit))
            return
        if kind == "mean":
            value = round(float(col_s.mean()), 2)
        elif kind == "max":
            value = round(float(col_s.max()), 2)
        elif kind == "min":
            value = round(float(col_s.min()), 2)
        elif kind == "sum":
            value = round(float(col_s.sum()), 2)
        change = _pct_change(df, col)
        kpis.append(
            KPI(
                label=label,
                value=value,
                unit=unit,
                change=change,
                change_label=(f"{change:+.1f}%" if change is not None else None),
            )
        )

    add("Average Rainfall", None, "mm", "rainfall", "mean")
    add("Average Temperature", None, "°C", "temperature", "mean")
    add("Highest Yield", None, "kg", "yield", "max")
    add("Lowest Yield", None, "kg", "yield", "min")
    add("Total Production", None, "t", "production", "sum")
    add("Average Soil Moisture", None, "%", "soil_moisture", "mean")
    return kpis


# ---------------------------------------------------------------------------
# Analytical capabilities
# ---------------------------------------------------------------------------
def analyze_current_conditions(
    df: pd.DataFrame, location_id: str | None = None
) -> list[Insight]:
    """Report the latest observation for each available weather metric."""
    if df.empty:
        return [
            _make_insight(
                "current_conditions", None, "No data available.", severity="info"
            )
        ]

    insights: list[Insight] = []
    date_col = _col(df, ["record_date", "date"])
    if date_col is None:
        return insights

    start, end = _get_time_bounds(df)
    latest_idx = df[date_col].idxmax()
    latest = df.loc[latest_idx]

    metric_map = {
        "rainfall": ("rainfall", "mm", ["rainfall", "rainfall_mm"]),
        "temperature": ("temperature", "°C", ["temperature", "temperature_c"]),
        "humidity": ("humidity", "%", ["humidity", "humidity_pct"]),
        "soil_moisture": ("soil_moisture", "%", ["soil_moisture", "soil_moisture_pct"]),
    }

    for metric_name, (_, unit, col_candidates) in metric_map.items():
        col = _col(df, col_candidates)
        if col is None:
            continue
        value = _safe_float(latest.get(col))
        if value is None:
            continue

        insights.append(
            _make_insight(
                type="current_conditions",
                metric=col,
                message=f"Current {metric_name.replace('_', ' ')} is {value}{unit}.",
                severity="info",
                magnitude=value,
                input_variables={
                    "location_id": location_id,
                    "metric": col,
                    "latest_timestamp": str(latest.get(date_col)),
                },
                time_range={"start": start, "end": end},
                calculation_method="latest_value",
                result={
                    "value": value,
                    "unit": unit,
                    "timestamp": str(latest.get(date_col)),
                },
                confidence=1.0,
                source="rule",
            )
        )
    return insights


def analyze_temperature_trends(
    df: pd.DataFrame, start: str | None = None, end: str | None = None
) -> list[Insight]:
    """Detect increasing or decreasing temperature trends using linear regression."""
    insights: list[Insight] = []
    col = _col(df, ["temperature", "temperature_c"])
    date_col = _col(df, ["record_date", "date"])
    if col is None or date_col is None:
        return insights

    sub = df[[date_col, col]].dropna().sort_values(date_col)
    if len(sub) < 3:
        return [
            _make_insight(
                "trend",
                col,
                "Insufficient data for temperature trend analysis.",
                severity="info",
            )
        ]

    start, end = _get_time_bounds(sub)
    x_vals = pd.to_datetime(sub[date_col]).map(datetime.toordinal).values
    y_vals = sub[col].values
    n = len(x_vals)
    x_mean = np.mean(x_vals)
    y_mean = np.mean(y_vals)
    numerator = np.sum((x_vals - x_mean) * (y_vals - y_mean))
    denominator = np.sum((x_vals - x_mean) ** 2)
    if denominator == 0:
        return insights

    slope = numerator / denominator
    intercept = y_mean - slope * x_mean
    ss_res = np.sum((y_vals - (slope * x_vals + intercept)) ** 2)
    ss_tot = np.sum((y_vals - y_mean) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

    trend_direction = (
        "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
    )
    magnitude = abs(round(slope * 30, 2))

    if abs(slope) < 0.01:
        return insights

    severity = (
        "info" if abs(slope) < 0.05 else "warning" if abs(slope) < 0.1 else "critical"
    )
    message = (
        f"Temperature shows a {trend_direction} trend over the period "
        f"with an approximate change of {magnitude}°C per month."
    )

    insights.append(
        _make_insight(
            type="trend",
            metric=col,
            message=message,
            severity=severity,
            magnitude=magnitude,
            input_variables={"data_points": n, "slope": round(slope, 4)},
            time_range={"start": start, "end": end},
            calculation_method="linear_regression (numpy polyfit degree=1)",
            result={
                "slope": round(slope, 4),
                "intercept": round(intercept, 4),
                "r_squared": round(r_squared, 4),
                "trend_direction": trend_direction,
                "monthly_change_c": magnitude,
            },
            confidence=min(round(r_squared, 2), 1.0),
            source="rule",
        )
    )
    return insights


def analyze_rainfall_trends(
    df: pd.DataFrame, start: str | None = None, end: str | None = None
) -> list[Insight]:
    """Detect increasing or decreasing rainfall trends using linear regression."""
    insights: list[Insight] = []
    col = _col(df, ["rainfall", "rainfall_mm"])
    date_col = _col(df, ["record_date", "date"])
    if col is None or date_col is None:
        return insights

    sub = df[[date_col, col]].dropna().sort_values(date_col)
    if len(sub) < 3:
        return [
            _make_insight(
                "trend",
                col,
                "Insufficient data for rainfall trend analysis.",
                severity="info",
            )
        ]

    start, end = _get_time_bounds(sub)
    x_vals = pd.to_datetime(sub[date_col]).map(datetime.toordinal).values
    y_vals = sub[col].values
    n = len(x_vals)
    x_mean = np.mean(x_vals)
    y_mean = np.mean(y_vals)
    numerator = np.sum((x_vals - x_mean) * (y_vals - y_mean))
    denominator = np.sum((x_vals - x_mean) ** 2)
    if denominator == 0:
        return insights

    slope = numerator / denominator
    intercept = y_mean - slope * x_mean
    ss_res = np.sum((y_vals - (slope * x_vals + intercept)) ** 2)
    ss_tot = np.sum((y_vals - y_mean) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

    trend_direction = (
        "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
    )
    magnitude = abs(round(slope * 30, 2))

    if abs(slope) < 0.01:
        return insights

    severity = (
        "info" if abs(slope) < 0.5 else "warning" if abs(slope) < 2.0 else "critical"
    )
    message = (
        f"Rainfall shows a {trend_direction} trend over the period "
        f"with an approximate change of {magnitude}mm per month."
    )

    insights.append(
        _make_insight(
            type="trend",
            metric=col,
            message=message,
            severity=severity,
            magnitude=magnitude,
            input_variables={"data_points": n, "slope": round(slope, 4)},
            time_range={"start": start, "end": end},
            calculation_method="linear_regression (numpy polyfit degree=1)",
            result={
                "slope": round(slope, 4),
                "intercept": round(intercept, 4),
                "r_squared": round(r_squared, 4),
                "trend_direction": trend_direction,
                "monthly_change_mm": magnitude,
            },
            confidence=min(round(r_squared, 2), 1.0),
            source="rule",
        )
    )
    return insights


def detect_anomalies(df: pd.DataFrame, z_threshold: float = 2.0) -> list[Insight]:
    """Detect simple anomalies using z-scores for numeric columns."""
    insights: list[Insight] = []
    numeric_cols = [
        c
        for c in [
            "rainfall",
            "rainfall_mm",
            "temperature",
            "temperature_c",
            "humidity",
            "humidity_pct",
            "soil_moisture",
            "soil_moisture_pct",
            "yield",
            "yield_kg_per_ha",
            "production",
            "production_tonnes",
        ]
        if c in df.columns
    ]

    for col in numeric_cols:
        s = pd.to_numeric(df[col], errors="coerce").dropna()
        if len(s) < 3:
            continue
        mean = s.mean()
        std = s.std(ddof=0)
        if std == 0:
            continue
        z_scores = (s - mean) / std
        anomalies = s[abs(z_scores) > z_threshold]
        if anomalies.empty:
            continue

        for idx, value in anomalies.items():
            z = abs(z_scores[idx])
            severity = "warning" if z < 3 else "critical"
            insights.append(
                _make_insight(
                    type="anomaly",
                    metric=col,
                    message=f"Anomalous {col.replace('_', ' ')} value detected: {_safe_float(value)} (z-score: {round(z, 2)}).",
                    severity=severity,
                    magnitude=_safe_float(value),
                    input_variables={
                        "z_threshold": z_threshold,
                        "z_score": round(z, 2),
                    },
                    time_range={"start": None, "end": None},
                    calculation_method=f"z_score > {z_threshold} (mean={round(mean, 2)}, std={round(std, 2)})",
                    result={
                        "value": _safe_float(value),
                        "z_score": round(z, 2),
                        "mean": round(mean, 2),
                        "std": round(std, 2),
                    },
                    confidence=(
                        min(round(1.0 - (z_threshold / z), 2), 1.0)
                        if z > z_threshold
                        else 0.5
                    ),
                    source="rule",
                )
            )
    return insights


def check_thresholds(df: pd.DataFrame) -> list[Insight]:
    """Threshold-based warnings for agricultural metrics."""
    insights: list[Insight] = []
    thresholds = {
        "rainfall": {"low": 50, "high": 300, "unit": "mm", "name": "rainfall"},
        "temperature": {"low": 10, "high": 40, "unit": "°C", "name": "temperature"},
        "humidity": {"low": 30, "high": 90, "unit": "%", "name": "humidity"},
        "soil_moisture": {"low": 20, "high": 80, "unit": "%", "name": "soil moisture"},
    }

    for col, cfg in thresholds.items():
        actual_col = _col(df, [col, f"{col}_mm", f"{col}_c", f"{col}_pct"])
        if actual_col is None:
            continue
        s = pd.to_numeric(df[actual_col], errors="coerce").dropna()
        if s.empty:
            continue
        latest = s.iloc[-1]
        if latest < cfg["low"]:
            insights.append(
                _make_insight(
                    type="threshold",
                    metric=actual_col,
                    message=f"Low {cfg['name']} detected: {_safe_float(latest)}{cfg['unit']} (threshold: {cfg['low']}{cfg['unit']}).",
                    severity="warning",
                    magnitude=_safe_float(latest),
                    input_variables={
                        "threshold_low": cfg["low"],
                        "threshold_high": cfg["high"],
                    },
                    time_range={"start": None, "end": None},
                    calculation_method=f"latest_value < {cfg['low']}",
                    result={
                        "value": _safe_float(latest),
                        "threshold": cfg["low"],
                        "breach": "low",
                    },
                    confidence=1.0,
                    source="rule",
                )
            )
        elif latest > cfg["high"]:
            insights.append(
                _make_insight(
                    type="threshold",
                    metric=actual_col,
                    message=f"High {cfg['name']} detected: {_safe_float(latest)}{cfg['unit']} (threshold: {cfg['high']}{cfg['unit']}).",
                    severity="warning",
                    magnitude=_safe_float(latest),
                    input_variables={
                        "threshold_low": cfg["low"],
                        "threshold_high": cfg["high"],
                    },
                    time_range={"start": None, "end": None},
                    calculation_method=f"latest_value > {cfg['high']}",
                    result={
                        "value": _safe_float(latest),
                        "threshold": cfg["high"],
                        "breach": "high",
                    },
                    confidence=1.0,
                    source="rule",
                )
            )
    return insights


def compare_time_periods(
    df: pd.DataFrame,
    period1_start: str,
    period1_end: str,
    period2_start: str,
    period2_end: str,
) -> list[Insight]:
    """Compare metrics between two time periods."""
    insights: list[Insight] = []
    date_col = _col(df, ["record_date", "date"])
    if date_col is None:
        return insights

    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    p1 = df[(df[date_col] >= period1_start) & (df[date_col] <= period1_end)]
    p2 = df[(df[date_col] >= period2_start) & (df[date_col] <= period2_end)]

    if p1.empty or p2.empty:
        return [
            _make_insight(
                "comparison",
                None,
                "Insufficient data for one or both periods.",
                severity="info",
            )
        ]

    metrics = [
        "rainfall",
        "temperature",
        "humidity",
        "soil_moisture",
        "yield",
        "production",
    ]
    for metric in metrics:
        col = _col(
            df,
            [
                metric,
                f"{metric}_mm",
                f"{metric}_c",
                f"{metric}_pct",
                f"{metric}_kg_per_ha",
                f"{metric}_tonnes",
            ],
        )
        if col is None:
            continue
        avg1 = _mean(p1, col)
        avg2 = _mean(p2, col)
        if avg1 is None or avg2 is None or avg1 == 0:
            continue

        pct_change = round((avg2 - avg1) / avg1 * 100, 1)
        direction = "increased" if pct_change > 0 else "decreased"
        severity = (
            "info"
            if abs(pct_change) < 10
            else "warning" if abs(pct_change) < 25 else "critical"
        )

        insights.append(
            _make_insight(
                type="comparison",
                metric=col,
                message=f"{metric.replace('_', ' ').title()} {direction} by {abs(pct_change):.1f}% between the two periods.",
                severity=severity,
                magnitude=abs(pct_change),
                input_variables={
                    "period1": {
                        "start": period1_start,
                        "end": period1_end,
                        "average": avg1,
                    },
                    "period2": {
                        "start": period2_start,
                        "end": period2_end,
                        "average": avg2,
                    },
                },
                time_range={"start": period1_start, "end": period2_end},
                calculation_method="period_average_comparison",
                result={
                    "period1_avg": avg1,
                    "period2_avg": avg2,
                    "pct_change": pct_change,
                    "direction": direction,
                },
                confidence=1.0,
                source="rule",
            )
        )
    return insights


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------
def generate_insights(
    df: pd.DataFrame, location_id: str | None = None
) -> list[Insight]:
    """Generate all applicable deterministic insights from a DataFrame."""
    if df.empty:
        return [
            _make_insight(
                "info",
                None,
                "No data available for the selected filters.",
                severity="info",
            )
        ]

    insights: list[Insight] = []
    insights.extend(analyze_current_conditions(df, location_id))
    insights.extend(analyze_temperature_trends(df))
    insights.extend(analyze_rainfall_trends(df))
    insights.extend(detect_anomalies(df))
    insights.extend(check_thresholds(df))
    return insights
