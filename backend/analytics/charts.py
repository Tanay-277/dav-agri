from __future__ import annotations

from typing import Any, cast

import pandas as pd


def _series(df: pd.DataFrame, x: str, y: str) -> tuple[list[str], list[float]]:
    """Aggregate y by x, returning sorted (labels, values)."""
    if x not in df.columns or y not in df.columns:
        return [], []
    sub = df[[x, y]].dropna()
    if sub.empty:
        return [], []
    grouped = sub.groupby(x, as_index=False)[y].mean()
    grouped = grouped.sort_values(x)
    return (
        grouped[x].astype(str).tolist(),
        [round(float(v), 2) for v in grouped[y].tolist()],
    )


def line_chart(df: pd.DataFrame) -> dict[str, Any]:
    """Trend analysis: rainfall & temperature over time."""
    x_col = (
        "date" if "date" in df.columns else ("year" if "year" in df.columns else None)
    )
    if x_col is None:
        return {"title": "Trend Analysis", "labels": [], "series": []}
    series = []
    for metric, name in (("rainfall", "Rainfall"), ("temperature", "Temperature")):
        s_labels, values = _series(df, x_col, metric)
        if s_labels:
            series.append({"name": name, "labels": s_labels, "values": values})
    labels: list[str] = cast(list[str], series[0]["labels"]) if series else []
    return {"title": "Trend Analysis", "labels": labels, "series": series}


def bar_chart(df: pd.DataFrame, metric: str = "production") -> dict[str, Any]:
    """State-wise metric comparison."""
    labels, values = _series(df, "state", metric)
    return {"title": "State Comparison", "labels": labels, "values": values}


def scatter_chart(df: pd.DataFrame) -> dict[str, Any]:
    """Rainfall vs Yield scatter points."""
    result: dict[str, Any] = {"title": "Rainfall vs Yield", "points": []}
    if {"rainfall", "yield"}.issubset(df.columns):
        sub = df[["rainfall", "yield"]].dropna()
        result["points"] = [
            {"x": float(r), "y": float(y)}
            for r, y in zip(sub["rainfall"], sub["yield"])
        ]
    return result


def heatmap_data(df: pd.DataFrame) -> dict[str, Any]:
    """Correlation matrix for numeric columns."""
    numeric = df.select_dtypes(include="number")
    if numeric.shape[1] < 2:
        return {"title": "Correlation", "columns": [], "matrix": []}
    corr = numeric.corr()
    return {
        "title": "Correlation Matrix",
        "columns": [str(c) for c in corr.columns],
        "matrix": [[round(float(v), 3) for v in row] for row in corr.values.tolist()],
    }


def pie_chart(df: pd.DataFrame) -> dict[str, Any]:
    """Crop distribution."""
    if "crop" not in df.columns:
        return {"title": "Crop Distribution", "labels": [], "values": []}
    counts = df["crop"].value_counts()
    return {
        "title": "Crop Distribution",
        "labels": [str(c) for c in counts.index],
        "values": [int(v) for v in counts.values],
    }
