from __future__ import annotations

import pytest

from database.repositories.agricultural import AgriculturalRepository
from database.repositories.insights import InsightRepository
from database.repositories.locations import LocationRepository
from database.repositories.queries import QueryLogRepository
from database.repositories.sources import DataSourceRepository
from database.repositories.weather import WeatherRepository


def _seed_location(
    repo: LocationRepository, location_id: str = "punjab_ludhiana"
) -> None:
    repo.upsert(
        {
            "location_id": location_id,
            "state": "Punjab",
            "district": "Ludhiana",
            "latitude": 30.9,
            "longitude": 75.85,
        }
    )


def _seed_source(repo: DataSourceRepository, source_id: str = "csv") -> None:
    repo.upsert(
        {
            "source_id": source_id,
            "name": "Local CSV Dataset",
            "provider_type": "csv",
            "is_active": 1,
        }
    )


class TestLocationRepository:
    def test_insert_and_find(self, test_db):
        repo = LocationRepository()
        repo.insert(
            {
                "location_id": "punjab_ludhiana",
                "state": "Punjab",
                "district": "Ludhiana",
                "latitude": 30.9,
                "longitude": 75.85,
            }
        )
        row = repo.find_by_id("punjab_ludhiana")
        assert row is not None
        assert row["state"] == "Punjab"
        assert row["district"] == "Ludhiana"

    def test_upsert_updates_existing(self, test_db):
        repo = LocationRepository()
        repo.insert(
            {
                "location_id": "punjab_ludhiana",
                "state": "Punjab",
                "district": "Ludhiana",
            }
        )
        repo.upsert(
            {
                "location_id": "punjab_ludhiana",
                "state": "Punjab",
                "district": "Ludhiana",
                "latitude": 30.9,
                "longitude": 75.85,
            }
        )
        row = repo.find_by_id("punjab_ludhiana")
        assert row["latitude"] == 30.9

    def test_find_by_state(self, test_db):
        repo = LocationRepository()
        repo.insert({"location_id": "p_l", "state": "Punjab", "district": "L"})
        repo.insert({"location_id": "m_l", "state": "Maharashtra", "district": "M"})
        rows = repo.find_by_state("Punjab")
        assert len(rows) == 1
        assert rows[0]["location_id"] == "p_l"

    def test_search_by_state_and_district(self, test_db):
        repo = LocationRepository()
        repo.insert({"location_id": "p_l", "state": "Punjab", "district": "Ludhiana"})
        repo.insert({"location_id": "p_j", "state": "Punjab", "district": "Jalandhar"})
        rows = repo.search(state="Punjab", district="Ludhiana")
        assert len(rows) == 1
        assert rows[0]["location_id"] == "p_l"


class TestDataSourceRepository:
    def test_seed_data_source_exists(self, test_db):
        repo = DataSourceRepository()
        row = repo.find_by_id("csv")
        assert row is not None
        assert row["name"] == "Local CSV Dataset"

    def test_get_active(self, test_db):
        repo = DataSourceRepository()
        repo.insert(
            {
                "source_id": "test",
                "name": "Test",
                "provider_type": "csv",
                "is_active": 1,
            }
        )
        active = repo.get_active()
        assert len(active) >= 1
        assert any(s["source_id"] == "test" for s in active)


class TestWeatherRepository:
    def test_bulk_insert_and_get_current(self, test_db):
        repo = WeatherRepository()
        _seed_location(LocationRepository())
        _seed_source(DataSourceRepository())
        records = [
            {
                "location_id": "punjab_ludhiana",
                "source_id": "csv",
                "timestamp": "2022-09-08T00:00:00",
                "record_date": "2022-09-08",
                "data_classification": "historical",
                "rainfall_mm": 117.9,
                "temperature_c": 27.4,
            },
            {
                "location_id": "punjab_ludhiana",
                "source_id": "csv",
                "timestamp": "2022-09-09T00:00:00",
                "record_date": "2022-09-09",
                "data_classification": "historical",
                "rainfall_mm": 50.0,
                "temperature_c": 25.0,
            },
        ]
        repo.bulk_insert(records)
        current = repo.get_current("punjab_ludhiana")
        assert current is not None
        assert current["record_date"] == "2022-09-09"

    def test_get_forecast(self, test_db):
        repo = WeatherRepository()
        _seed_location(LocationRepository())
        _seed_source(DataSourceRepository())
        records = [
            {
                "location_id": "punjab_ludhiana",
                "source_id": "csv",
                "timestamp": "2024-01-01T00:00:00",
                "record_date": "2024-01-01",
                "data_classification": "forecast",
                "precipitation_probability_pct": 30.0,
            },
            {
                "location_id": "punjab_ludhiana",
                "source_id": "csv",
                "timestamp": "2024-01-02T00:00:00",
                "record_date": "2024-01-02",
                "data_classification": "forecast",
                "precipitation_probability_pct": 60.0,
            },
        ]
        repo.bulk_insert(records)
        forecast = repo.get_forecast("punjab_ludhiana", days=2)
        assert len(forecast) == 2
        assert forecast[0]["data_classification"] == "forecast"

    def test_get_historical_range(self, test_db):
        repo = WeatherRepository()
        _seed_location(LocationRepository())
        _seed_source(DataSourceRepository())
        records = [
            {
                "location_id": "punjab_ludhiana",
                "source_id": "csv",
                "timestamp": f"2022-{m:02d}-01T00:00:00",
                "record_date": f"2022-{m:02d}-01",
                "data_classification": "historical",
                "rainfall_mm": 100.0,
            }
            for m in range(1, 13)
        ]
        repo.bulk_insert(records)
        rows = repo.get_historical(
            "punjab_ludhiana", start="2022-06-01", end="2022-08-31"
        )
        assert len(rows) == 3

    def test_rainfall_trends(self, test_db):
        repo = WeatherRepository()
        _seed_location(LocationRepository())
        _seed_source(DataSourceRepository())
        records = [
            {
                "location_id": "punjab_ludhiana",
                "source_id": "csv",
                "timestamp": f"2022-09-{d:02d}T00:00:00",
                "record_date": f"2022-09-{d:02d}",
                "data_classification": "historical",
                "rainfall_mm": float(d * 10),
            }
            for d in range(1, 4)
        ]
        repo.bulk_insert(records)
        trends = repo.get_rainfall_trends("punjab_ludhiana", "2022-09-01", "2022-09-03")
        assert len(trends) == 3
        assert trends[0]["total_rainfall"] == 10.0

    def test_temperature_trends(self, test_db):
        repo = WeatherRepository()
        _seed_location(LocationRepository())
        _seed_source(DataSourceRepository())
        records = [
            {
                "location_id": "punjab_ludhiana",
                "source_id": "csv",
                "timestamp": f"2022-09-{d:02d}T00:00:00",
                "record_date": f"2022-09-{d:02d}",
                "data_classification": "historical",
                "temperature_c": float(20 + d),
            }
            for d in range(1, 4)
        ]
        repo.bulk_insert(records)
        trends = repo.get_temperature_trends(
            "punjab_ludhiana", "2022-09-01", "2022-09-03"
        )
        assert len(trends) == 3
        assert trends[0]["min_temp"] == 21.0

    def test_compare_locations(self, test_db):
        repo = WeatherRepository()
        for loc in ["punjab_ludhiana", "maharashtra_pune"]:
            _seed_location(LocationRepository(), loc)
        _seed_source(DataSourceRepository())
        records = [
            {
                "location_id": loc,
                "source_id": "csv",
                "timestamp": "2022-09-08T00:00:00",
                "record_date": "2022-09-08",
                "data_classification": "historical",
                "rainfall_mm": 100.0 if loc == "punjab_ludhiana" else 50.0,
            }
            for loc in ["punjab_ludhiana", "maharashtra_pune"]
        ]
        repo.bulk_insert(records)
        comparison = repo.compare_locations(
            ["punjab_ludhiana", "maharashtra_pune"],
            "rainfall_mm",
            "2022-09-01",
            "2022-09-30",
        )
        assert len(comparison) == 2


class TestAgriculturalRepository:
    def test_bulk_insert_and_query(self, test_db):
        repo = AgriculturalRepository()
        _seed_location(LocationRepository())
        _seed_source(DataSourceRepository())
        records = [
            {
                "location_id": "punjab_ludhiana",
                "source_id": "csv",
                "record_date": "2022-09-08",
                "crop": "Rice",
                "yield_kg_per_ha": 400.0,
                "production_tonnes": 500.0,
                "area_ha": 100.0,
            }
        ]
        repo.bulk_insert(records)
        rows = repo.get_by_crop("Rice")
        assert len(rows) == 1
        assert rows[0]["crop"] == "Rice"

    def test_crop_summary(self, test_db):
        repo = AgriculturalRepository()
        _seed_location(LocationRepository())
        _seed_source(DataSourceRepository())
        records = [
            {
                "location_id": "punjab_ludhiana",
                "source_id": "csv",
                "record_date": f"2022-09-{d:02d}",
                "crop": "Rice",
                "yield_kg_per_ha": 400.0 + d,
                "production_tonnes": 500.0,
                "area_ha": 100.0,
            }
            for d in range(1, 4)
        ]
        repo.bulk_insert(records)
        summary = repo.get_crop_summary("Rice", "2022-09-01", "2022-09-30")
        assert summary is not None
        assert summary["record_count"] == 3
        assert summary["avg_yield"] == pytest.approx(402.0)


class TestQueryLogRepository:
    def test_insert_and_recent(self, test_db):
        repo = QueryLogRepository()
        query_id = repo.insert(
            {
                "session_id": "s1",
                "user_id": "u1",
                "filters_json": '{"crop": "Rice"}',
                "result_summary": '{"kpi_count": 3}',
                "response_time_ms": 120,
            }
        )
        assert query_id > 0
        recent = repo.get_recent(limit=1)
        assert len(recent) == 1
        assert recent[0]["session_id"] == "s1"

    def test_get_by_session(self, test_db):
        repo = QueryLogRepository()
        repo.insert({"session_id": "s1", "filters_json": "{}", "result_summary": "{}"})
        repo.insert({"session_id": "s1", "filters_json": "{}", "result_summary": "{}"})
        repo.insert({"session_id": "s2", "filters_json": "{}", "result_summary": "{}"})
        rows = repo.get_by_session("s1")
        assert len(rows) == 2


class TestInsightRepository:
    def test_bulk_insert_and_query(self, test_db):
        repo = InsightRepository()
        query_repo = QueryLogRepository()
        query_id = query_repo.insert(
            {
                "session_id": "s1",
                "filters_json": "{}",
                "result_summary": "{}",
            }
        )
        records = [
            {
                "query_id": query_id,
                "insight_type": "trend",
                "metric": "rainfall_mm",
                "severity": "info",
                "message": "Rainfall increasing",
                "source": "rule",
            },
            {
                "query_id": query_id,
                "insight_type": "anomaly",
                "metric": "temperature_c",
                "severity": "warning",
                "message": "Temperature spike detected",
                "source": "rule",
            },
        ]
        repo.bulk_insert(records)
        insights = repo.get_by_query(query_id)
        assert len(insights) == 2
        assert insights[0]["insight_type"] == "trend"

    def test_get_by_location(self, test_db):
        repo = InsightRepository()
        _seed_location(LocationRepository())
        repo.insert(
            {
                "query_id": None,
                "location_id": "punjab_ludhiana",
                "insight_type": "comparison",
                "metric": "yield_kg_per_ha",
                "message": "High yield",
                "source": "rule",
            }
        )
        rows = repo.get_by_location("punjab_ludhiana")
        assert len(rows) == 1
        assert rows[0]["message"] == "High yield"
