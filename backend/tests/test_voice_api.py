from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from main import app as _fastapi_app


client = TestClient(_fastapi_app)


class TestVoiceAPI:
    """End-to-end tests for the unified voice API."""

    # ------------------------------------------------------------------ #
    # Scenario 1: "Will it rain tomorrow?"
    # ------------------------------------------------------------------ #
    def test_scenario_1_will_it_rain_tomorrow(self):
        response = client.post("/api/v1/voice/query", json={
            "query": "Will it rain tomorrow?",
            "language": "en",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["structured_query"]["intent"] == "forecast"
        assert data["structured_query"]["time_period"]["relative"] == "tomorrow"
        assert len(data["insights"]) > 0

    def test_scenario_1_voice_query(self):
        response = client.post("/api/v1/voice/query", data={
            "language": "en",
            "auto_detect": "false",
            "noise_level": "clean",
        }, files={"audio": ("test.wav", b"fake-audio-bytes", "audio/wav")})
        assert response.status_code in (200, 422)

    # ------------------------------------------------------------------ #
    # Scenario 2: "Is tomorrow hotter than today?"
    # ------------------------------------------------------------------ #
    def test_scenario_2_comparison_query(self):
        response = client.post("/api/v1/voice/query", json={
            "query": "Is tomorrow hotter than today?",
            "language": "en",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["structured_query"]["intent"] == "comparison"
        assert len(data["insights"]) > 0

    # ------------------------------------------------------------------ #
    # Scenario 3: Supported question in another target language (Hindi)
    # ------------------------------------------------------------------ #
    def test_scenario_3_hindi_query(self):
        response = client.post("/api/v1/voice/query", json={
            "query": "Kya kal barish hogi?",
            "language": "hi",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["structured_query"]["intent"] == "forecast"
        assert data["structured_query"]["language"] == "hi"
        assert len(data["insights"]) > 0

    # ------------------------------------------------------------------ #
    # Scenario 4: Ambiguous question
    # ------------------------------------------------------------------ #
    def test_scenario_4_ambiguous_query(self):
        response = client.post("/api/v1/voice/query", json={
            "query": "Weather?",
            "language": "en",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["structured_query"]["needs_clarification"] is True
        assert len(data["structured_query"]["clarification_options"]) > 0

    # ------------------------------------------------------------------ #
    # Scenario 5: Unsupported question
    # ------------------------------------------------------------------ #
    def test_scenario_5_unsupported_query(self):
        response = client.post("/api/v1/voice/query", json={
            "query": "What is the stock price of wheat?",
            "language": "en",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["structured_query"]["intent"] == "unsupported"
        assert data["structured_query"]["unsupported_reason"] is not None

    # ------------------------------------------------------------------ #
    # Numerical consistency verification
    # ------------------------------------------------------------------ #
    def test_numerical_consistency_through_pipeline(self):
        query_response = client.post("/api/v1/voice/query", json={
            "query": "Temperature in Punjab",
            "language": "en",
        })
        assert query_response.status_code == 200
        query_data = query_response.json()
        insights = query_data["insights"]
        assert len(insights) > 0
        insight = insights[0]
        assert "result" in insight
        result = insight["result"]
        assert "value" in result or "values" in result
        speech_response = client.post("/api/v1/voice/speech-response", json={
            "insight": insight,
            "language": "en",
            "voice_gender": "female",
            "rate": 1.0,
        })
        assert speech_response.status_code == 200
        speech_data = speech_response.json()
        assert speech_data["success"] is True
        assert speech_data["text"]
        if "value" in result:
            assert str(result["value"]) in speech_data["text"]
        elif "values" in result:
            for v in result["values"].values():
                if v is not None:
                    assert str(v) in speech_data["text"]

    # ------------------------------------------------------------------ #
    # Health check
    # ------------------------------------------------------------------ #
    def test_health(self):
        response = client.get("/api/v1/voice/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "supported_languages" in data
        assert "stt_providers" in data
        assert "tts_providers" in data

    # ------------------------------------------------------------------ #
    # Locations
    # ------------------------------------------------------------------ #
    def test_locations(self):
        response = client.get("/api/v1/voice/locations")
        assert response.status_code == 200
        data = response.json()
        assert "states" in data
        assert "districts" in data
        assert "crops" in data
        assert len(data["states"]) > 0

    # ------------------------------------------------------------------ #
    # Weather endpoint
    # ------------------------------------------------------------------ #
    def test_weather(self):
        response = client.get("/api/v1/voice/weather?state=Punjab")
        assert response.status_code == 200
        data = response.json()
        assert "kpis" in data
        assert "rows" in data

    # ------------------------------------------------------------------ #
    # Forecast endpoint
    # ------------------------------------------------------------------ #
    def test_forecast(self):
        response = client.get("/api/v1/voice/forecast?state=Punjab&days=7")
        assert response.status_code == 200
        data = response.json()
        assert "kpis" in data
        assert data["forecast_days"] == 7

    # ------------------------------------------------------------------ #
    # Structured insight endpoint
    # ------------------------------------------------------------------ #
    def test_insight(self):
        response = client.get("/api/v1/voice/insight?state=Punjab&crop=Wheat")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "type" in data[0]
            assert "message" in data[0]

    # ------------------------------------------------------------------ #
    # Speech response endpoint
    # ------------------------------------------------------------------ #
    def test_speech_response(self):
        insight = {
            "type": "current_weather",
            "location": "Punjab",
            "value": 32,
            "values": {"rain_probability": 20, "rainfall": 10},
        }
        response = client.post("/api/v1/voice/speech-response", json={
            "insight": insight,
            "language": "en",
            "voice_gender": "female",
            "rate": 1.0,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "text" in data
        assert "Punjab" in data["text"]
        assert "32" in data["text"]

    # ------------------------------------------------------------------ #
    # Error handling: empty query
    # ------------------------------------------------------------------ #
    def test_error_empty_query(self):
        response = client.post("/api/v1/voice/query", json={
            "query": "",
            "language": "en",
        })
        assert response.status_code == 422

    # ------------------------------------------------------------------ #
    # Error handling: unsupported language
    # ------------------------------------------------------------------ #
    def test_error_unsupported_language(self):
        response = client.post("/api/v1/voice/query", json={
            "query": "Hello",
            "language": "fr",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["structured_query"]["intent"] == "general_query"

    # ------------------------------------------------------------------ #
    # Multilingual speech response
    # ------------------------------------------------------------------ #
    def test_multilingual_speech_response(self):
        insight = {
            "type": "current_weather",
            "location": "Punjab",
            "value": 30,
            "values": {"rain_probability": 10, "rainfall": 5},
        }
        for lang in ["hi", "ta", "te", "kn", "mr", "bn"]:
            response = client.post("/api/v1/voice/speech-response", json={
                "insight": insight,
                "language": lang,
                "voice_gender": "female",
            })
            assert response.status_code == 200, f"Failed for {lang}"
            data = response.json()
            assert data["success"] is True
            assert data["language"] == lang
