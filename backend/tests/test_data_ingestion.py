from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from data_ingestion.base import WeatherRecord
from data_ingestion.cache import get_cached, init_cache, set_cached
from data_ingestion.csv_provider import CSVProvider
from data_ingestion.errors import (
    APIError,
)
from data_ingestion.normalizer import (
    normalize_openmeteo_daily,
)
from data_ingestion.openmeteo_provider import OpenMeteoProvider


@pytest.fixture(autouse=True)
def _clear_cache() -> None:
    """Ensure weather API cache is empty before each test."""
    init_cache()
    from data_ingestion.cache import prune_stale

    prune_stale(0)


class TestWeatherRecord:
    def test_valid_record(self) -> None:
        ts = datetime(2024, 1, 1, 12, 0, 0)
        rec = WeatherRecord(
            timestamp=ts,
            location_id="punjab_ludhiana",
            latitude=30.9,
            longitude=75.8,
            rainfall_mm=12.5,
            temperature_c=22.0,
            humidity_pct=65.0,
            soil_moisture_pct=40.0,
            wind_speed_kmh=10.0,
            cloud_cover_okta=3.0,
            precipitation_probability_pct=30.0,
            source="open-meteo",
        )
        assert rec.rainfall_mm == 12.5
        assert rec.source == "open-meteo"

    def test_none_values_allowed(self) -> None:
        rec = WeatherRecord(
            timestamp=datetime(2024, 1, 1),
            location_id="test",
            source="csv",
        )
        assert rec.rainfall_mm is None
        assert rec.temperature_c is None


class TestCSVProvider:
    @patch("database.data._load_dataset")
    def test_loads_records(self, mock_load: MagicMock) -> None:
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
                "state": ["Punjab", "Punjab"],
                "district": ["Ludhiana", "Ludhiana"],
                "crop": ["Wheat", "Wheat"],
                "rainfall": [10.0, 5.0],
                "temperature": [20.0, 22.0],
                "humidity": [60.0, 65.0],
                "soil_moisture": [40.0, 42.0],
                "yield": [3000.0, 3100.0],
                "production": [100.0, 110.0],
                "area": [50.0, 50.0],
            }
        )
        mock_load.return_value = df
        provider = CSVProvider()
        records = provider.fetch_historical(
            "punjab_ludhiana", None, None, "2024-01-01", "2024-01-02"
        )
        assert len(records) == 2
        assert records[0].rainfall_mm == 10.0
        assert records[0].source == "csv"
        assert records[0].location_id == "punjab_ludhiana"

    @patch("database.data._load_dataset")
    def test_empty_when_no_matches(self, mock_load: MagicMock) -> None:
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-01"]),
                "state": ["Karnataka"],
                "district": ["Bangalore"],
                "crop": ["Rice"],
            }
        )
        mock_load.return_value = df
        provider = CSVProvider()
        records = provider.fetch_historical(
            "punjab_ludhiana", None, None, "2024-01-01", "2024-01-02"
        )
        assert len(records) == 0

    @patch("database.data._load_dataset")
    def test_current_returns_latest(self, mock_load: MagicMock) -> None:
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
                "state": ["Punjab", "Punjab"],
                "district": ["Ludhiana", "Ludhiana"],
                "rainfall": [10.0, 5.0],
            }
        )
        mock_load.return_value = df
        provider = CSVProvider()
        rec = provider.fetch_current("punjab_ludhiana", None, None)
        assert rec is not None
        assert rec.rainfall_mm == 5.0

    @patch("database.data._load_dataset")
    def test_as_dataframe(self, mock_load: MagicMock) -> None:
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-01"]),
                "state": ["Punjab"],
                "district": ["Ludhiana"],
                "rainfall": [10.0],
            }
        )
        mock_load.return_value = df
        provider = CSVProvider()
        records = provider.fetch_historical(
            "punjab_ludhiana", None, None, "2024-01-01", "2024-01-02"
        )
        out = provider.as_dataframe(records)
        assert len(out) == 1
        assert "rainfall_mm" in out.columns
        assert "source" in out.columns


class TestOpenMeteoNormalizer:
    def test_normalizes_historical(self) -> None:
        payload = {
            "daily": {
                "time": ["2024-01-01", "2024-01-02"],
                "temperature_2m_mean": [15.0, 18.0],
                "precipitation_sum": [0.0, 5.0],
                "relative_humidity_2m_mean": [60.0, 70.0],
                "wind_speed_10m_max": [10.0, 15.0],
                "cloud_cover_mean": [2.0, 5.0],
            }
        }
        records = normalize_openmeteo_daily(payload, "test_loc", 30.9, 75.8)
        assert len(records) == 2
        assert records[0].rainfall_mm == 0.0
        assert records[0].temperature_c == 15.0
        assert records[0].humidity_pct == 60.0
        assert records[0].source == "open-meteo"
        assert records[0].latitude == 30.9

    def test_handles_missing_fields(self) -> None:
        payload = {
            "daily": {
                "time": ["2024-01-01"],
                "temperature_2m_mean": [None],
                "precipitation_sum": [None],
            }
        }
        records = normalize_openmeteo_daily(payload, "test_loc", None, None)
        assert len(records) == 1
        assert records[0].rainfall_mm is None
        assert records[0].temperature_c is None
        assert records[0].source == "open-meteo"

    def test_validates_ranges(self) -> None:
        payload = {
            "daily": {
                "time": ["2024-01-01"],
                "temperature_2m_mean": [100.0],
                "precipitation_sum": [-5.0],
            }
        }
        records = normalize_openmeteo_daily(payload, "test_loc", None, None)
        assert records[0].temperature_c is None
        assert records[0].rainfall_mm is None

    def test_skips_invalid_dates(self) -> None:
        payload = {
            "daily": {
                "time": ["not-a-date"],
                "temperature_2m_mean": [15.0],
            }
        }
        records = normalize_openmeteo_daily(payload, "test_loc", None, None)
        assert len(records) == 0


class TestOpenMeteoProvider:
    @patch("data_ingestion.openmeteo_provider.httpx.Client")
    def test_fetch_historical_success(self, mock_client_cls: MagicMock) -> None:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "daily": {
                "time": ["2024-01-01"],
                "temperature_2m_mean": [15.0],
                "precipitation_sum": [0.0],
                "relative_humidity_2m_mean": [60.0],
                "wind_speed_10m_max": [10.0],
                "cloud_cover_mean": [2.0],
            }
        }
        mock_client.request.return_value = mock_resp

        provider = OpenMeteoProvider()
        records = provider.fetch_historical(
            "test", 30.9, 75.8, "2024-01-01", "2024-01-01"
        )
        assert len(records) == 1
        assert records[0].temperature_c == 15.0

    @patch("data_ingestion.openmeteo_provider.httpx.Client")
    def test_retries_on_429(self, mock_client_cls: MagicMock) -> None:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        rate_resp = MagicMock()
        rate_resp.status_code = 429
        rate_resp.headers = {"Retry-After": "1"}

        ok_resp = MagicMock()
        ok_resp.status_code = 200
        ok_resp.json.return_value = {
            "daily": {
                "time": ["2024-01-01"],
                "temperature_2m_mean": [15.0],
                "precipitation_sum": [0.0],
                "relative_humidity_2m_mean": [60.0],
                "wind_speed_10m_max": [10.0],
                "cloud_cover_mean": [2.0],
            }
        }

        mock_client.request.side_effect = [rate_resp, ok_resp]

        provider = OpenMeteoProvider()
        records = provider.fetch_historical(
            "test", 30.9, 75.8, "2024-01-01", "2024-01-01"
        )
        assert len(records) == 1
        assert mock_client.request.call_count == 2

    @patch("data_ingestion.openmeteo_provider.httpx.Client")
    def test_raises_on_auth_failure(self, mock_client_cls: MagicMock) -> None:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.text = "Unauthorized"
        mock_client.request.return_value = mock_resp

        provider = OpenMeteoProvider()
        with pytest.raises(APIError):
            provider.fetch_historical("test", 30.9, 75.8, "2024-01-01", "2024-01-01")

    def test_forecast_raises_not_implemented(self) -> None:
        provider = OpenMeteoProvider()
        with pytest.raises(NotImplementedError):
            provider.fetch_forecast("test", 30.9, 75.8, days=3)


class TestCache:
    def test_set_and_get(self) -> None:
        init_cache()
        set_cached("csv", "loc1", "2024-01-01", {"temp": 20.0})
        payload = get_cached("csv", "loc1", "2024-01-01", ttl_hours=24)
        assert payload == {"temp": 20.0}

    def test_cache_miss(self) -> None:
        init_cache()
        payload = get_cached("csv", "nonexistent", "2024-01-01", ttl_hours=24)
        assert payload is None

    def test_stale_cache_returns_none(self) -> None:
        init_cache()
        set_cached("csv", "loc1", "2024-01-01", {"temp": 20.0})
        # Request with TTL of 0 hours -> should be stale.
        payload = get_cached("csv", "loc1", "2024-01-01", ttl_hours=0)
        assert payload is None
