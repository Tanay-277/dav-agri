from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from main import app as _fastapi_app
from text_to_speech.schemas import (
    SynthesisResponse,
)

client = TestClient(_fastapi_app)


@pytest.fixture(autouse=True)
def _ensure_tts_providers():
    from text_to_speech.provider import (
        EdgeTTSProvider,
        MockTTSProvider,
        _registry,
        register_tts_provider,
    )
    _registry._providers.clear()
    edge = EdgeTTSProvider()
    if edge._available:
        register_tts_provider(edge)
    register_tts_provider(MockTTSProvider())
    yield
    _registry._providers.clear()


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
            "provider_name": "mock",
        })
        assert speech_response.status_code == 200
        audio_text = speech_response.headers.get("X-Audio-Text", "")
        assert audio_text
        if "value" in result:
            assert str(result["value"]) in audio_text
        elif "values" in result:
            for v in result["values"].values():
                if v is not None:
                    assert str(v) in audio_text

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
            "provider_name": "mock",
        })
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/mpeg"
        audio_text = response.headers.get("X-Audio-Text", "")
        assert "Punjab" in audio_text
        assert "32" in audio_text

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
                "provider_name": "mock",
            })
            assert response.status_code == 200, f"Failed for {lang}"
            assert response.headers["content-type"] == "audio/mpeg"
            assert response.headers.get("X-Audio-Language") == lang


class TestSpeechResponseProviderSelection:
    def test_speech_response_uses_configured_provider_by_default(self):
        mock_settings = MagicMock()
        mock_settings.TTS_PROVIDER = "edge"
        mock_settings.TTS_ALLOW_MOCK = True

        mock_synthesis = SynthesisResponse(
            success=True,
            provider="edge",
            audio_bytes=b"REAL_AUDIO_BYTES",
            content_type="audio/mpeg",
            duration_ms=1000,
        )
        mock_provider = MagicMock()
        mock_provider.synthesize = AsyncMock(return_value=mock_synthesis)

        with patch("api.voice_api.get_settings", return_value=mock_settings):
            with patch("text_to_speech.provider.get_tts_provider", return_value=mock_provider):
                response = client.post("/api/v1/voice/speech-response", json={
                    "insight": {
                        "type": "current_weather",
                        "location": "Punjab",
                        "value": 32,
                    },
                    "language": "en",
                })
                assert response.status_code == 200
                assert response.headers["X-Audio-Provider"] == "edge"
                assert response.content == b"REAL_AUDIO_BYTES"

    def test_speech_response_rejects_mock_in_production(self):
        mock_settings = MagicMock()
        mock_settings.TTS_PROVIDER = "edge"
        mock_settings.TTS_ALLOW_MOCK = False

        with patch("api.voice_api.get_settings", return_value=mock_settings):
            response = client.post("/api/v1/voice/speech-response", json={
                "insight": {
                    "type": "current_weather",
                    "location": "Punjab",
                    "value": 32,
                },
                "language": "en",
                "provider_name": "mock",
            })
            assert response.status_code == 500
            body = response.json()
            assert "not allowed in production" in body["detail"]

    def test_speech_response_rejects_unavailable_provider(self):
        mock_settings = MagicMock()
        mock_settings.TTS_PROVIDER = "edge"
        mock_settings.TTS_ALLOW_MOCK = True

        mock_provider = MagicMock()
        mock_provider._available = False

        with patch("api.voice_api.get_settings", return_value=mock_settings):
            with patch("text_to_speech.provider.get_tts_provider", return_value=mock_provider):
                response = client.post("/api/v1/voice/speech-response", json={
                    "insight": {
                        "type": "current_weather",
                        "location": "Punjab",
                        "value": 32,
                    },
                    "language": "en",
                })
                assert response.status_code == 500
                body = response.json()
                assert "not available" in body["detail"]

    def test_speech_response_unsupported_language_fallback(self):
        response = client.post("/api/v1/voice/speech-response", json={
            "insight": {
                "type": "current_weather",
                "location": "Punjab",
                "value": 32,
            },
            "language": "xx",
            "provider_name": "mock",
        })
        assert response.status_code == 200
        assert response.headers["X-Audio-Language"] == "en"

    def test_speech_response_with_real_edge_provider(self):
        insight = {
            "type": "current_weather",
            "location": "Punjab",
            "value": 32,
            "values": {"rain_probability": 20, "rainfall": 10},
        }
        response = client.post("/api/v1/voice/speech-response", json={
            "insight": insight,
            "language": "en",
            "provider_name": "edge",
        })
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/mpeg"
        assert response.headers["X-Audio-Provider"] == "edge"
        assert len(response.content) > 1000
        assert response.content.startswith(b"\xff\xf3")
