from __future__ import annotations

import pandas as pd

from analytics.engine import _mean as _avg  # noqa: F401
from models.schemas import Recommendation


def generate_recommendations(df: pd.DataFrame) -> list[Recommendation]:
    """Rule-based recommendations from analytical signals."""
    if df.empty:
        return [
            Recommendation(
                condition="no-data",
                message="Load a dataset to generate recommendations.",
                priority="low",
            )
        ]

    recs: list[Recommendation] = []
    rain = _avg(df, "rainfall")
    temp = _avg(df, "temperature")
    humidity = _avg(df, "humidity")
    soil = _avg(df, "soil_moisture")

    if rain is not None and temp is not None:
        if rain < 100 and temp > 30:
            recs.append(
                Recommendation(
                    condition="rainfall_down && temperature_up",
                    message=(
                        "Low rainfall with high temperatures detected. "
                        "Irrigation is recommended to maintain crop health."
                    ),
                    priority="high",
                    action="irrigation",
                )
            )

    if humidity is not None and humidity < 50:
        recs.append(
            Recommendation(
                condition="humidity_low",
                message=(
                    "Humidity is low. Monitor soil moisture closely and "
                    "consider mulching to reduce evaporation."
                ),
                priority="medium",
                action="monitor_soil",
            )
        )

    if rain is not None and rain < 80:
        recs.append(
            Recommendation(
                condition="rainfall_low",
                message="Rainfall is below typical levels. Plan supplemental water.",
                priority="medium",
                action="irrigation_plan",
            )
        )

    if soil is not None and soil < 25:
        recs.append(
            Recommendation(
                condition="soil_moisture_low",
                message="Soil moisture is low. Schedule irrigation promptly.",
                priority="high",
                action="irrigation",
            )
        )

    if not recs:
        recs.append(
            Recommendation(
                condition="default",
                message="Conditions look healthy. Continue current farm management.",
                priority="low",
                action="maintain",
            )
        )
    return recs
