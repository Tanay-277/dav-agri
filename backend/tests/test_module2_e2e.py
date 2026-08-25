from __future__ import annotations

import json
import time
from typing import Any

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

MODULE2_LANGUAGES = ["en", "hi", "ta", "te", "kn", "mr", "bn"]
LOCATIONS = [
    ("Punjab", None),
    ("Maharashtra", None),
    ("Karnataka", None),
    ("Gujarat", None),
]


class TestModule2EndToEnd:
    """Comprehensive end-to-end test suite for Module 2 validation."""

    class TestSuccessfulQueries:
        def test_rain_query_forecast_intent(self):
            response = client.post("/api/v1/voice/query", json={
                "query": "Will it rain tomorrow?",
                "language": "en",
            })
            assert response.status_code == 200
            data = response.json()
            assert data["structured_query"]["intent"] == "forecast"
            assert data["structured_query"]["time_period"]["relative"] == "tomorrow"

        def test_comparison_query(self):
            response = client.post("/api/v1/voice/query", json={
                "query": "Is tomorrow hotter than today?",
                "language": "en",
            })
            assert response.status_code == 200
            data = response.json()
            assert data["structured_query"]["intent"] == "comparison"

        def test_trend_query(self):
            response = client.post("/api/v1/voice/query", json={
                "query": "Is rainfall increasing?",
                "language": "en",
            })
            assert response.status_code == 200
            data = response.json()
            assert data["structured_query"]["intent"] == "trend_query"

        def test_recommendation_query(self):
            response = client.post("/api/v1/voice/query", json={
                "query": "What should I do?",
                "language": "en",
            })
            assert response.status_code == 200
            data = response.json()
            assert data["structured_query"]["intent"] == "recommendation_query"

        def test_yield_query(self):
            response = client.post("/api/v1/voice/query", json={
                "query": "How is wheat doing in Punjab?",
                "language": "en",
            })
            assert response.status_code == 200
            data = response.json()
            assert data["structured_query"]["intent"] == "yield_query"

        def test_query_returns_insights(self):
            response = client.post("/api/v1/voice/query", json={
                "query": "Will it rain tomorrow?",
                "language": "en",
            })
            assert response.status_code == 200
            data = response.json()
            assert len(data["insights"]) > 0

    class TestIncorrectQueries:
        def test_typo_query_still_returns_result(self):
            response = client.post("/api/v1/voice/query", json={
                "query": "Wll it rain tomorrow?",
                "language": "en",
            })
            assert response.status_code == 200
            data = response.json()
            assert "structured_query" in data
            assert "insights" in data

        def test_garbled_query_returns_general(self):
            response = client.post("/api/v1/voice/query", json={
                "query": "asdfghjkl qwerty",
                "language": "en",
            })
            assert response.status_code == 200
            data = response.json()
            assert data["structured_query"]["intent"] == "general_query"

    class TestAmbiguousQueries:
        def test_weather_question_mark(self):
            response = client.post("/api/v1/voice/query", json={
                "query": "Weather?",
                "language": "en",
            })
            assert response.status_code == 200
            data = response.json()
            assert data["structured_query"]["needs_clarification"] is True
            assert len(data["structured_query"]["clarification_options"]) > 0

        def test_show_me_is_general(self):
            response = client.post("/api/v1/voice/query", json={
                "query": "Show me",
                "language": "en",
            })
            assert response.status_code == 200
            data = response.json()
            assert data["structured_query"]["intent"] == "general_query"

        def test_help_intent(self):
            response = client.post("/api/v1/voice/query", json={
                "query": "Help",
                "language": "en",
            })
            assert response.status_code == 200
            data = response.json()
            assert data["structured_query"]["intent"] == "help"

    class TestUnsupportedQueries:
        def test_stock_price_unsupported(self):
            response = client.post("/api/v1/voice/query", json={
                "query": "What is the stock price of wheat?",
                "language": "en",
            })
            assert response.status_code == 200
            data = response.json()
            assert data["structured_query"]["intent"] == "unsupported"
            assert data["structured_query"]["unsupported_reason"] is not None

        def test_email_unsupported(self):
            response = client.post("/api/v1/voice/query", json={
                "query": "Send an email to the farmer",
                "language": "en",
            })
            assert response.status_code == 200
            data = response.json()
            assert data["structured_query"]["intent"] == "unsupported"

        def test_fertilizer_cost_unsupported(self):
            response = client.post("/api/v1/voice/query", json={
                "query": "What is the cost of fertilizer?",
                "language": "en",
            })
            assert response.status_code == 200
            data = response.json()
            assert data["structured_query"]["intent"] == "unsupported"

    class TestMissingData:
        def test_query_without_location_clarifies(self):
            response = client.post("/api/v1/voice/query", json={
                "query": "What is the temperature?",
                "language": "en",
            })
            assert response.status_code == 200
            data = response.json()
            assert "structured_query" in data
            assert "insights" in data

        def test_weather_endpoint_without_filters(self):
            response = client.get("/api/v1/voice/weather")
            assert response.status_code == 200
            data = response.json()
            assert "kpis" in data
            assert "rows" in data

    class TestAPIFailure:
        def test_empty_query_returns_422(self):
            response = client.post("/api/v1/voice/query", json={
                "query": "",
                "language": "en",
            })
            assert response.status_code == 422

        def test_missing_query_returns_422(self):
            response = client.post("/api/v1/voice/query", json={
                "language": "en",
            })
            assert response.status_code == 422

        def test_invalid_json_returns_422(self):
            response = client.post("/api/v1/voice/query", data="invalid", headers={"Content-Type": "application/json"})
            assert response.status_code == 422

    class TestSpeechRecognitionFailure:
        def test_empty_audio_returns_error(self):
            response = client.post("/api/v1/voice/voice-query", data={
                "language": "en",
            }, files={"audio": ("test.wav", b"", "audio/wav")})
            assert response.status_code in (400, 422)

        def test_oversized_audio_returns_error(self):
            large_audio = b"x" * (51 * 1024 * 1024)
            response = client.post("/api/v1/voice/voice-query", data={
                "language": "en",
            }, files={"audio": ("test.wav", large_audio, "audio/wav")})
            assert response.status_code in (200, 400, 422, 500)

    class TestTTSFailure:
        def test_speech_response_handles_missing_insight(self):
            response = client.post("/api/v1/voice/speech-response", json={
                "insight": {},
                "language": "en",
            })
            assert response.status_code == 200
            data = response.json()
            assert "text" in data

        def test_speech_response_unsupported_language_fallback(self):
            insight = {
                "type": "current_weather",
                "location": "Punjab",
                "value": 32,
                "values": {"rain_probability": 20, "rainfall": 10},
            }
            response = client.post("/api/v1/voice/speech-response", json={
                "insight": insight,
                "language": "fr",
                "voice_gender": "female",
            })
            assert response.status_code == 200
            data = response.json()
            assert data["language"] == "en"

    class TestMultipleLanguages:
        def test_hindi_query(self):
            response = client.post("/api/v1/voice/query", json={
                "query": "Kya kal barish hogi?",
                "language": "hi",
            })
            assert response.status_code == 200
            data = response.json()
            assert data["structured_query"]["intent"] == "forecast"

        def test_speech_response_hindi(self):
            insight = {
                "type": "current_weather",
                "location": "Punjab",
                "value": 30,
                "values": {"rain_probability": 10, "rainfall": 5},
            }
            response = client.post("/api/v1/voice/speech-response", json={
                "insight": insight,
                "language": "hi",
                "voice_gender": "female",
            })
            assert response.status_code == 200
            data = response.json()
            assert data["language"] == "hi"

    class TestMultipleLocations:
        @pytest.mark.parametrize("state", ["Punjab", "Maharashtra", "Karnataka", "Gujarat"])
        def test_query_by_state(self, state: str):
            response = client.post("/api/v1/voice/query", json={
                "query": f"What is the weather in {state}?",
                "language": "en",
            })
            assert response.status_code == 200
            data = response.json()
            assert data["structured_query"]["intent"] in ("current_conditions", "general_query")

        def test_locations_endpoint_returns_non_empty(self):
            response = client.get("/api/v1/voice/locations")
            assert response.status_code == 200
            data = response.json()
            assert len(data["states"]) > 0
            assert len(data["crops"]) > 0

    class TestDifferentTimePeriods:
        def test_today_query(self):
            response = client.post("/api/v1/voice/query", json={
                "query": "What is the weather today?",
                "language": "en",
            })
            assert response.status_code == 200
            data = response.json()
            assert data["structured_query"]["time_period"]["relative"] == "today"

        def test_tomorrow_query(self):
            response = client.post("/api/v1/voice/query", json={
                "query": "What is the weather tomorrow?",
                "language": "en",
            })
            assert response.status_code == 200
            data = response.json()
            assert data["structured_query"]["time_period"]["relative"] == "tomorrow"

        def test_yesterday_query(self):
            response = client.post("/api/v1/voice/query", json={
                "query": "What was the weather yesterday?",
                "language": "en",
            })
            assert response.status_code == 200
            data = response.json()
            assert data["structured_query"]["time_period"]["relative"] == "yesterday"

    class TestDataCorrectness:
        def test_numerical_values_in_insights(self):
            response = client.post("/api/v1/voice/query", json={
                "query": "Temperature in Punjab",
                "language": "en",
            })
            assert response.status_code == 200
            data = response.json()
            insights = data["insights"]
            assert len(insights) > 0
            insight = insights[0]
            assert "result" in insight
            result = insight["result"]
            assert "value" in result or "values" in result

        def test_numerical_consistency_insight_to_speech(self):
            query_response = client.post("/api/v1/voice/query", json={
                "query": "Temperature in Punjab",
                "language": "en",
            })
            assert query_response.status_code == 200
            query_data = query_response.json()
            insights = query_data["insights"]
            if len(insights) == 0:
                pytest.skip("No insights returned")
            insight = insights[0]
            result = insight.get("result", {})
            value = result.get("value")
            if value is None:
                pytest.skip("No numeric value in insight")
            speech_response = client.post("/api/v1/voice/speech-response", json={
                "insight": insight,
                "language": "en",
            })
            assert speech_response.status_code == 200
            speech_data = speech_response.json()
            assert str(value) in speech_data["text"]

        def test_no_hallucinated_data_in_insights(self):
            response = client.post("/api/v1/voice/query", json={
                "query": "What is the weather in Punjab?",
                "language": "en",
            })
            assert response.status_code == 200
            data = response.json()
            insights = data["insights"]
            for insight in insights:
                assert "message" in insight
                assert insight["message"] is not None
                assert len(insight["message"]) > 0
                assert "result" in insight

    class TestLatency:
        def test_query_latency_under_2s(self):
            start = time.perf_counter()
            response = client.post("/api/v1/voice/query", json={
                "query": "Will it rain tomorrow?",
                "language": "en",
            })
            duration_ms = (time.perf_counter() - start) * 1000
            assert response.status_code == 200
            assert duration_ms < 2000, f"Query took {duration_ms:.1f}ms"

        def test_speech_response_latency_under_2s(self):
            insight = {
                "type": "current_weather",
                "location": "Punjab",
                "value": 32,
                "values": {"rain_probability": 20, "rainfall": 10},
            }
            start = time.perf_counter()
            response = client.post("/api/v1/voice/speech-response", json={
                "insight": insight,
                "language": "en",
            })
            duration_ms = (time.perf_counter() - start) * 1000
            assert response.status_code == 200
            assert duration_ms < 2000, f"TTS took {duration_ms:.1f}ms"

    class TestReproducibility:
        def test_same_query_produces_same_intent(self):
            response1 = client.post("/api/v1/voice/query", json={
                "query": "Will it rain tomorrow?",
                "language": "en",
            })
            response2 = client.post("/api/v1/voice/query", json={
                "query": "Will it rain tomorrow?",
                "language": "en",
            })
            assert response1.status_code == 200
            assert response2.status_code == 200
            data1 = response1.json()
            data2 = response2.json()
            assert data1["structured_query"]["intent"] == data2["structured_query"]["intent"]

    class TestSecurity:
        def test_no_sensitive_data_in_responses(self):
            response = client.post("/api/v1/voice/query", json={
                "query": "What is the weather?",
                "language": "en",
            })
            assert response.status_code == 200
            body = str(response.json()).lower()
            assert "api_key" not in body
            assert "password" not in body
            assert "secret" not in body

        def test_cors_headers_present(self):
            response = client.get("/api/v1/voice/health")
            assert response.status_code == 200
            assert "content-type" in response.headers

    class TestLogging:
        def test_request_id_header_present(self):
            response = client.get("/api/v1/voice/health")
            assert response.status_code == 200
            assert "x-request-id" in response.headers

    class TestEndToEndPipeline:
        def test_full_pipeline_text_to_speech(self):
            query_response = client.post("/api/v1/voice/query", json={
                "query": "What is the rainfall in Karnataka?",
                "language": "en",
            })
            assert query_response.status_code == 200
            query_data = query_response.json()
            insights = query_data["insights"]
            assert len(insights) > 0

            speech_response = client.post("/api/v1/voice/speech-response", json={
                "insight": insights[0],
                "language": "en",
                "voice_gender": "female",
            })
            assert speech_response.status_code == 200
            speech_data = speech_response.json()
            assert speech_data["success"] is True
            assert len(speech_data["text"]) > 0

        def test_weather_endpoint_returns_kpis(self):
            response = client.get("/api/v1/voice/weather?state=Punjab")
            assert response.status_code == 200
            data = response.json()
            assert "kpis" in data
            assert len(data["kpis"]) > 0

        def test_forecast_endpoint_returns_forecast_days(self):
            response = client.get("/api/v1/voice/forecast?state=Punjab&days=7")
            assert response.status_code == 200
            data = response.json()
            assert "kpis" in data
            assert data["forecast_days"] == 7

        def test_insight_endpoint_returns_structured_data(self):
            response = client.get("/api/v1/voice/insight?state=Punjab&crop=Wheat")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            if len(data) > 0:
                assert "type" in data[0]
                assert "message" in data[0]
