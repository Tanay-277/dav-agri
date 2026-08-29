from __future__ import annotations

import os
from functools import lru_cache

from core.config import get_settings


class DataIngestionSettings:
    """Settings for the data ingestion layer."""

    def __init__(self) -> None:
        s = get_settings()
        self.provider: str = os.getenv("WEATHER_PROVIDER", "csv")
        self.openmeteo_url: str = os.getenv(
            "OPEN_METEO_URL", "https://archive-api.open-meteo.com/v1"
        )
        self.openmeteo_forecast_url: str = os.getenv(
            "OPEN_METEO_FORECAST_URL", "https://api.open-meteo.com/v1"
        )
        self.openmeteo_geocoding_url: str = os.getenv(
            "OPEN_METEO_GEOCODING_URL", "https://geocoding-api.open-meteo.com/v1"
        )
        self.timeout_seconds: int = int(os.getenv("WEATHER_API_TIMEOUT_S", "10"))
        self.cache_ttl_hours: int = int(os.getenv("WEATHER_CACHE_TTL_HOURS", "24"))
        self.forecast_cache_ttl_hours: int = int(
            os.getenv("WEATHER_FORECAST_CACHE_TTL_HOURS", "3")
        )
        self.max_retries: int = int(os.getenv("WEATHER_API_MAX_RETRIES", "3"))
        self.dataset_dir = s.DATASET_DIR
        self.dataset_file = s.DATASET_FILE
        self.debug: bool = s.DEBUG


@lru_cache(maxsize=1)
def get_data_ingestion_settings() -> DataIngestionSettings:
    return DataIngestionSettings()
