from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def _reset_dataset_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    from database import data

    monkeypatch.setattr(data, "_load_dataset", data._load_dataset.__wrapped__)


def test_health() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "app" in body


def test_dataset_status() -> None:
    response = client.get("/api/v1/dataset/status")
    assert response.status_code == 200
    body = response.json()
    assert body["loaded"] is True
    assert body["rows"] > 500
    assert "date" in body["columns"]


def test_filters() -> None:
    response = client.get("/api/v1/filters")
    assert response.status_code == 200
    body = response.json()
    assert "crop" in body
    assert "state" in body
    assert "district" in body
    assert len(body["crop"]) > 0
    assert len(body["state"]) > 0


def test_dashboard_default() -> None:
    response = client.get("/api/v1/dashboard")
    assert response.status_code == 200
    body = response.json()
    assert "charts" in body
    assert "kpis" in body
    assert "filters" in body
    assert "line" in body["charts"]
    assert "bar" in body["charts"]
    assert "scatter" in body["charts"]
    assert "heatmap" in body["charts"]
    assert "pie" in body["charts"]
    assert len(body["kpis"]) == 6
    assert body["metadata"]["rows"] > 500


def test_dashboard_with_filters() -> None:
    response = client.get(
        "/api/v1/dashboard", params={"crop": "Wheat", "state": "Punjab"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["metadata"]["rows"] >= 1
    for kpi in body["kpis"]:
        assert "label" in kpi
        assert "value" in kpi
        assert "unit" in kpi


def test_insights() -> None:
    response = client.get("/api/v1/insights", params={"crop": "Rice"})
    assert response.status_code == 200
    body = response.json()
    assert "insights" in body
    assert isinstance(body["insights"], list)
    assert len(body["insights"]) > 0
    for insight in body["insights"]:
        assert "type" in insight
        assert "message" in insight
        assert "severity" in insight


def test_insights_no_data() -> None:
    response = client.get("/api/v1/insights", params={"crop": "NonExistentCrop"})
    assert response.status_code == 200
    body = response.json()
    assert len(body["insights"]) == 1
    assert body["insights"][0]["severity"] == "info"


def test_story() -> None:
    response = client.get("/api/v1/story", params={"crop": "Wheat"})
    assert response.status_code == 200
    body = response.json()
    assert "story" in body
    assert "summary" in body
    assert "reasons" in body
    assert "recommendations" in body
    assert "source" in body
    assert len(body["story"]) > 0


def test_recommendations() -> None:
    response = client.get("/api/v1/recommendations", params={"state": "Rajasthan"})
    assert response.status_code == 200
    body = response.json()
    assert "recommendations" in body
    assert isinstance(body["recommendations"], list)
    assert len(body["recommendations"]) > 0
    for rec in body["recommendations"]:
        assert "condition" in rec
        assert "message" in rec
        assert "priority" in rec


def test_export_json() -> None:
    response = client.post("/api/v1/export", params={"format": "json"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"


def test_export_pdf() -> None:
    response = client.post("/api/v1/export", params={"format": "pdf"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"


def test_research_task_log() -> None:
    response = client.post(
        "/api/v1/research/task-log",
        json={
            "task_id": "weather_outlook",
            "condition": "conventional",
            "user_id": "user_123",
            "completed": True,
            "duration_ms": 45000,
            "voice_used": False,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"


def test_research_survey() -> None:
    response = client.post(
        "/api/v1/research/survey",
        json={
            "task_id": "weather_outlook",
            "condition": "conventional",
            "user_id": "user_123",
            "comprehension_score": 3,
            "trust_score": 4,
            "sus_score": 75,
            "feedback": "Clear and easy to use.",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"


def test_research_condition() -> None:
    response = client.get(
        "/api/v1/research/condition", params={"condition": "voice-story"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["condition"] == "voice-story"
