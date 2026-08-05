from __future__ import annotations

from typing import Any

import pandas as pd

from models.schemas import KPI


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
