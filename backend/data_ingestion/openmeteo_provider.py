from __future__ import annotations

import time
from datetime import datetime
from typing import Any

import httpx

from core.logging import get_logger
from data_ingestion.base import BaseProvider, WeatherRecord
from data_ingestion.cache import get_cached, set_cached
from data_ingestion.errors import APIError, DataIngestionError, RateLimitError
from data_ingestion.normalizer import normalize_openmeteo_daily

logger = get_logger(__name__)

# Open-Meteo archive API variables we request.
_ARCHIVE_VARIABLES = [
    "temperature_2m_mean",
    "precipitation_sum",
    "relative_humidity_2m_mean",
    "wind_speed_10m_max",
    "cloud_cover_mean",
]


class OpenMeteoProvider(BaseProvider):
    """Open-Meteo API provider for historical weather data."""

    name = "open-meteo"

    def __init__(self) -> None:
        s = get_data_ingestion_settings()
        self.base_url = s.openmeteo_url.rstrip("/")
        self.geocoding_url = s.openmeteo_geocoding_url.rstrip("/")
        self.timeout = s.timeout_seconds
        self.max_retries = s.max_retries
        self._client = httpx.Client(timeout=self.timeout)

    def _request(
        self, method: str, url: str, params: dict[str, Any] | None = None
    ) -> httpx.Response:
        """Make HTTP request with retry and backoff."""
        last_exc: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                resp = self._client.request(method, url, params=params)
            except httpx.TimeoutException as exc:
                last_exc = exc
                wait = 2**attempt
                logger.warning(
                    "Open-Meteo timeout (attempt %d/%d): %s",
                    attempt + 1,
                    self.max_retries,
                    exc,
                )
                time.sleep(wait)
                continue
            except httpx.NetworkError as exc:
                last_exc = exc
                logger.error("Open-Meteo network error: %s", exc)
                raise DataIngestionError(f"Network error contacting Open-Meteo: {exc}")

            if resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", 1))
                logger.warning(
                    "Open-Meteo rate limited. Retrying after %ds (attempt %d/%d)",
                    retry_after,
                    attempt + 1,
                    self.max_retries,
                )
                time.sleep(min(retry_after, 10))
                continue
            if resp.status_code >= 500:
                wait = 2**attempt
                logger.warning(
                    "Open-Meteo server error %d (attempt %d/%d). Retrying in %ds",
                    resp.status_code,
                    attempt + 1,
                    self.max_retries,
                    wait,
                )
                time.sleep(wait)
                continue
            if resp.status_code == 401 or resp.status_code == 403:
                raise APIError(
                    "Open-Meteo authentication failed",
                    status_code=resp.status_code,
                    body=resp.text,
                )
            resp.raise_for_status()
            return resp

        if last_exc:
            raise DataIngestionError(
                f"Open-Meteo request failed after {self.max_retries} retries: {last_exc}"
            )
        raise RateLimitError(
            f"Open-Meteo rate limit exceeded after {self.max_retries} retries"
        )

    def geocode(self, state: str, district: str) -> tuple[float, float]:
        """Resolve state + district to latitude/longitude using Open-Meteo geocoding."""
        query = f"{district.strip()}, {state.strip()}, India"
        url = f"{self.geocoding_url}/search"
        params = {"name": query, "count": 1, "language": "en", "format": "json"}
        resp = self._request("GET", url, params=params)
        data = resp.json()
        results = data.get("results") or []
        if not results:
            raise DataIngestionError(f"Geocoding failed for query: {query}")
        lat = float(results[0]["latitude"])
        lon = float(results[0]["longitude"])
        logger.info("Geocoded %s -> (%s, %s)", query, lat, lon)
        return lat, lon

    def fetch_historical(
        self,
        location_id: str,
        latitude: float | None,
        longitude: float | None,
        start_date: str,
        end_date: str,
    ) -> list[WeatherRecord]:
        if latitude is None or longitude is None:
            raise DataIngestionError(
                "Latitude and longitude are required for Open-Meteo provider"
            )

        cache_key_date = f"{start_date}/{end_date}"
        cached = get_cached(self.name, location_id, cache_key_date, ttl_hours=24)
        if cached is not None:
            logger.debug("Cache hit for Open-Meteo %s %s", location_id, cache_key_date)
            return normalize_openmeteo_daily(cached, location_id, latitude, longitude)

        url = f"{self.base_url}/archive"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "daily": ",".join(_ARCHIVE_VARIABLES),
            "timezone": "UTC",
        }
        resp = self._request("GET", url, params=params)
        payload = resp.json()

        set_cached(self.name, location_id, cache_key_date, payload)
        logger.info(
            "Fetched Open-Meteo archive for %s (%s to %s)",
            location_id,
            start_date,
            end_date,
        )
        return normalize_openmeteo_daily(payload, location_id, latitude, longitude)

    def fetch_current(
        self,
        location_id: str,
        latitude: float | None,
        longitude: float | None,
    ) -> WeatherRecord | None:
        if latitude is None or longitude is None:
            return None

        cached = get_cached(self.name, location_id, "current", ttl_hours=1)
        if cached is not None:
            records = normalize_openmeteo_daily(
                cached, location_id, latitude, longitude
            )
            return records[-1] if records else None

        url = f"{self.base_url}/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": "true",
            "timezone": "UTC",
        }
        try:
            resp = self._request("GET", url, params=params)
            payload = resp.json()
            cw = payload.get("current_weather", {})
            if not cw:
                return None

            record = WeatherRecord(
                timestamp=datetime.fromisoformat(
                    cw.get("time", datetime.utcnow().isoformat())
                ),
                location_id=location_id,
                latitude=latitude,
                longitude=longitude,
                temperature_c=cw.get("temperature"),
                wind_speed_kmh=cw.get("windspeed"),
                source="open-meteo",
                raw=payload,
            )
            return record
        except DataIngestionError as exc:
            logger.warning("Open-Meteo current weather fetch failed: %s", exc)
            return None

    def fetch_forecast(
        self,
        location_id: str,
        latitude: float | None,
        longitude: float | None,
        days: int = 3,
    ) -> list[WeatherRecord]:
        raise NotImplementedError("Open-Meteo forecast is deferred to post-MVRS")


def get_data_ingestion_settings():
    from data_ingestion.settings import get_data_ingestion_settings

    return get_data_ingestion_settings()
