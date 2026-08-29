from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from data_ingestion.base import WeatherRecord

logger = logging.getLogger(__name__)


def _to_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _validate_range(
    value: float | None, min_v: float, max_v: float, name: str
) -> float | None:
    if value is None:
        return None
    if not (min_v <= value <= max_v):
        logger.warning("Value out of range for %s: %s", name, value)
        return None
    return value


def normalize_openmeteo_daily(
    payload: dict[str, Any],
    location_id: str,
    latitude: float | None,
    longitude: float | None,
) -> list[WeatherRecord]:
    """Normalize Open-Meteo archive daily response to WeatherRecord list."""
    daily = payload.get("daily", {})
    time_list = daily.get("time", [])
    if not time_list:
        return []

    def _vals(key: str) -> list[float | None]:
        raw = daily.get(key)
        if raw is None:
            return [None] * len(time_list)
        return [_to_float(v) for v in raw]

    records: list[WeatherRecord] = []
    for idx, date_str in enumerate(time_list):
        try:
            timestamp = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=None)
        except ValueError:
            logger.warning("Invalid date in Open-Meteo response: %s", date_str)
            continue

        rainfall = _validate_range(
            _vals("precipitation_sum")[idx], 0, 500, "rainfall_mm"
        )
        temp = _validate_range(
            _vals("temperature_2m_mean")[idx], -10, 60, "temperature_c"
        )
        humidity = _validate_range(
            _vals("relative_humidity_2m_mean")[idx], 0, 100, "humidity_pct"
        )
        wind = _validate_range(
            _vals("wind_speed_10m_max")[idx], 0, 400, "wind_speed_kmh"
        )
        cloud = _validate_range(
            _vals("cloud_cover_mean")[idx], 0, 8, "cloud_cover_okta"
        )

        records.append(
            WeatherRecord(
                timestamp=timestamp,
                location_id=location_id,
                latitude=latitude,
                longitude=longitude,
                rainfall_mm=rainfall,
                temperature_c=temp,
                humidity_pct=humidity,
                soil_moisture_pct=None,
                wind_speed_kmh=wind,
                cloud_cover_okta=cloud,
                precipitation_probability_pct=None,
                source="open-meteo",
                raw={"daily": daily, "index": idx},
            )
        )
    return records


def normalize_openmeteo_forecast_daily(
    payload: dict[str, Any],
    location_id: str,
    latitude: float | None,
    longitude: float | None,
) -> list[WeatherRecord]:
    """Normalize Open-Meteo forecast daily response to WeatherRecord list."""
    daily = payload.get("daily", {})
    time_list = daily.get("time", [])
    if not time_list:
        return []

    def _vals(key: str) -> list[float | None]:
        raw = daily.get(key)
        if raw is None:
            return [None] * len(time_list)
        return [_to_float(v) for v in raw]

    records: list[WeatherRecord] = []
    for idx, date_str in enumerate(time_list):
        try:
            timestamp = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=None)
        except ValueError:
            logger.warning("Invalid date in Open-Meteo forecast response: %s", date_str)
            continue

        precip_prob = _validate_range(
            _vals("precipitation_probability_mean")[idx],
            0,
            100,
            "precipitation_probability_pct",
        )
        _temp_min = _validate_range(
            _vals("temperature_2m_min")[idx], -10, 60, "temperature_min_c"
        )
        _temp_max = _validate_range(
            _vals("temperature_2m_max")[idx], -10, 60, "temperature_max_c"
        )
        wind = _validate_range(
            _vals("wind_speed_10m_max")[idx], 0, 400, "wind_speed_kmh"
        )

        records.append(
            WeatherRecord(
                timestamp=timestamp,
                location_id=location_id,
                latitude=latitude,
                longitude=longitude,
                rainfall_mm=_to_float(_vals("precipitation_sum")[idx]),
                temperature_c=None,
                humidity_pct=_validate_range(
                    _vals("relative_humidity_2m_mean")[idx], 0, 100, "humidity_pct"
                ),
                soil_moisture_pct=None,
                wind_speed_kmh=wind,
                cloud_cover_okta=None,
                precipitation_probability_pct=precip_prob,
                source="open-meteo",
                raw={"daily": daily, "index": idx},
            )
        )
    return records
