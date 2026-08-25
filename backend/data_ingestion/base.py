from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class WeatherRecord(BaseModel):
    """Canonical weather record across all providers."""

    timestamp: datetime = Field(..., description="UTC timestamp of the observation")
    location_id: str = Field(
        ..., description="Normalized location identifier, e.g. 'punjab_ludhiana'"
    )
    latitude: float | None = Field(
        default=None, description="Decimal degrees, positive=N"
    )
    longitude: float | None = Field(
        default=None, description="Decimal degrees, positive=E"
    )
    rainfall_mm: float | None = Field(
        default=None, description="Total rainfall in millimeters"
    )
    temperature_c: float | None = Field(
        default=None, description="Air temperature in degrees Celsius"
    )
    humidity_pct: float | None = Field(
        default=None, description="Relative humidity percentage [0-100]"
    )
    soil_moisture_pct: float | None = Field(
        default=None, description="Soil moisture percentage [0-100]"
    )
    wind_speed_kmh: float | None = Field(default=None, description="Wind speed in km/h")
    cloud_cover_okta: float | None = Field(
        default=None, description="Cloud cover in oktas [0-8]"
    )
    precipitation_probability_pct: float | None = Field(
        default=None, description="Probability of precipitation [0-100]"
    )
    source: str = Field(..., description="Provider name: csv | open-meteo | nasa-power")
    raw: dict[str, Any] | None = Field(
        default=None, description="Original provider response for debugging"
    )

    model_config = {"use_enum_values": True}


class BaseProvider(ABC):
    """Abstract base class for weather data providers."""

    name: str = "base"

    @abstractmethod
    def fetch_historical(
        self,
        location_id: str,
        latitude: float | None,
        longitude: float | None,
        start_date: str,
        end_date: str,
    ) -> list[WeatherRecord]:
        """Fetch historical daily weather for a location and date range."""

    @abstractmethod
    def fetch_current(
        self,
        location_id: str,
        latitude: float | None,
        longitude: float | None,
    ) -> WeatherRecord | None:
        """Fetch current weather for a location."""

    def fetch_forecast(
        self,
        location_id: str,
        latitude: float | None,
        longitude: float | None,
        days: int = 3,
    ) -> list[WeatherRecord]:
        """Fetch forecast weather. Default: not implemented for MVRS."""
        raise NotImplementedError(
            f"{self.name} provider does not support forecast in MVRS"
        )
