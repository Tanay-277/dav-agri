from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from nlu.engine import QueryUnderstandingEngine
from nlu.schema import IntentCategory, TimePeriod, ComparisonSpec


@pytest.fixture
def engine() -> QueryUnderstandingEngine:
    return QueryUnderstandingEngine()


# ---------------------------------------------------------------------------
# Test queries organized by category
# ---------------------------------------------------------------------------
TEST_QUERIES: list[dict] = [
    # 1. Current conditions (10 queries)
    {"query": "What is the current weather in Punjab?", "expected_intent": IntentCategory.CURRENT_CONDITIONS, "expected_entities": {"state": "Punjab"}},
    {"query": "Current temperature in Ludhiana", "expected_intent": IntentCategory.TEMPERATURE_QUERY, "expected_entities": {"district": "Ludhiana", "state": "Punjab"}},
    {"query": "How hot is it today in Maharashtra?", "expected_intent": IntentCategory.TEMPERATURE_QUERY, "expected_entities": {"state": "Maharashtra"}},
    {"query": "What's the rainfall in Karnataka?", "expected_intent": IntentCategory.RAINFALL_QUERY, "expected_entities": {"state": "Karnataka"}},
    {"query": "Is it raining in Bangalore?", "expected_intent": IntentCategory.RAINFALL_QUERY, "expected_entities": {"district": "Bangalore", "state": "Karnataka"}},
    {"query": "Humidity level in Gujarat", "expected_intent": IntentCategory.HUMIDITY_QUERY, "expected_entities": {"state": "Gujarat"}},
    {"query": "Soil moisture status", "expected_intent": IntentCategory.SOIL_QUERY, "expected_entities": {}},
    {"query": "Wind speed in Tamil Nadu", "expected_intent": IntentCategory.WIND_QUERY, "expected_entities": {"state": "Tamil Nadu"}},
    {"query": "Weather conditions right now", "expected_intent": IntentCategory.CURRENT_CONDITIONS, "expected_entities": {}},
    {"query": "Present temperature at Pune", "expected_intent": IntentCategory.TEMPERATURE_QUERY, "expected_entities": {"district": "Pune", "state": "Maharashtra"}},

    # 2. Forecast queries (5 queries)
    {"query": "Will it rain tomorrow?", "expected_intent": IntentCategory.FORECAST, "expected_entities": {}},
    {"query": "What is the temperature forecast for next week?", "expected_intent": IntentCategory.FORECAST, "expected_entities": {}},
    {"query": "Will it be hot tomorrow in Punjab?", "expected_intent": IntentCategory.FORECAST, "expected_entities": {"state": "Punjab"}},
    {"query": "Expected rainfall in Maharashtra tomorrow", "expected_intent": IntentCategory.FORECAST, "expected_entities": {"state": "Maharashtra"}},
    {"query": "Is tomorrow going to be cold in Rajasthan?", "expected_intent": IntentCategory.FORECAST, "expected_entities": {"state": "Rajasthan"}},

    # 3. Historical queries (5 queries)
    {"query": "What was the weather like yesterday?", "expected_intent": IntentCategory.HISTORICAL_QUERY, "expected_entities": {}},
    {"query": "Temperature last week in Karnataka", "expected_intent": IntentCategory.HISTORICAL_QUERY, "expected_entities": {"state": "Karnataka"}},
    {"query": "Rainfall history for Gujarat", "expected_intent": IntentCategory.HISTORICAL_QUERY, "expected_entities": {"state": "Gujarat"}},
    {"query": "Past weather conditions in Coimbatore", "expected_intent": IntentCategory.HISTORICAL_QUERY, "expected_entities": {"district": "Coimbatore", "state": "Tamil Nadu"}},
    {"query": "What was the temperature last month?", "expected_intent": IntentCategory.HISTORICAL_QUERY, "expected_entities": {}},

    # 4. Comparison queries (5 queries)
    {"query": "Compare tomorrow with today", "expected_intent": IntentCategory.COMPARISON, "expected_entities": {}},
    {"query": "Is tomorrow hotter than today?", "expected_intent": IntentCategory.COMPARISON, "expected_entities": {}},
    {"query": "Compare rainfall this week vs last week", "expected_intent": IntentCategory.COMPARISON, "expected_entities": {}},
    {"query": "Temperature difference between Punjab and Maharashtra", "expected_intent": IntentCategory.COMPARISON, "expected_entities": {"state": "Punjab"}},
    {"query": "Which has more rain: Bangalore or Mysore?", "expected_intent": IntentCategory.COMPARISON, "expected_entities": {"district": "Bangalore", "state": "Karnataka"}},

    # 5. Trend queries (5 queries)
    {"query": "Is rainfall increasing?", "expected_intent": IntentCategory.TREND_QUERY, "expected_entities": {}},
    {"query": "Temperature trend over the last month", "expected_intent": IntentCategory.TREND_QUERY, "expected_entities": {}},
    {"query": "Is humidity going down in Gujarat?", "expected_intent": IntentCategory.TREND_QUERY, "expected_entities": {"state": "Gujarat"}},
    {"query": "Pattern of soil moisture over time", "expected_intent": IntentCategory.TREND_QUERY, "expected_entities": {}},
    {"query": "Is yield rising or falling for wheat?", "expected_intent": IntentCategory.TREND_QUERY, "expected_entities": {"crop": "Wheat"}},

    # 6. Threshold queries (5 queries)
    {"query": "Is soil moisture low?", "expected_intent": IntentCategory.THRESHOLD_QUERY, "expected_entities": {}},
    {"query": "Is it too hot today?", "expected_intent": IntentCategory.THRESHOLD_QUERY, "expected_entities": {}},
    {"query": "Is rainfall below normal in Punjab?", "expected_intent": IntentCategory.THRESHOLD_QUERY, "expected_entities": {"state": "Punjab"}},
    {"query": "Is temperature above 40 degrees?", "expected_intent": IntentCategory.THRESHOLD_QUERY, "expected_entities": {}},
    {"query": "Humidity level too high?", "expected_intent": IntentCategory.THRESHOLD_QUERY, "expected_entities": {}},

    # 7. Anomaly queries (5 queries)
    {"query": "Any unusual weather patterns?", "expected_intent": IntentCategory.ANOMALY_QUERY, "expected_entities": {}},
    {"query": "Is there an outlier in temperature data?", "expected_intent": IntentCategory.ANOMALY_QUERY, "expected_entities": {}},
    {"query": "Abnormal rainfall in Maharashtra", "expected_intent": IntentCategory.ANOMALY_QUERY, "expected_entities": {"state": "Maharashtra"}},
    {"query": "Strange weather patterns in Karnataka", "expected_intent": IntentCategory.ANOMALY_QUERY, "expected_entities": {"state": "Karnataka"}},
    {"query": "Any odd values in the dataset?", "expected_intent": IntentCategory.ANOMALY_QUERY, "expected_entities": {}},

    # 8. Recommendation queries (5 queries)
    {"query": "What should I do?", "expected_intent": IntentCategory.RECOMMENDATION_QUERY, "expected_entities": {}},
    {"query": "Should I irrigate wheat in Punjab?", "expected_intent": IntentCategory.RECOMMENDATION_QUERY, "expected_entities": {"crop": "Wheat", "state": "Punjab"}},
    {"query": "Advice for rice cultivation in Tamil Nadu", "expected_intent": IntentCategory.RECOMMENDATION_QUERY, "expected_entities": {"crop": "Rice", "state": "Tamil Nadu"}},
    {"query": "Recommendation for maize in Andhra Pradesh", "expected_intent": IntentCategory.RECOMMENDATION_QUERY, "expected_entities": {"crop": "Maize", "state": "Andhra Pradesh"}},
    {"query": "What action should I take for cotton?", "expected_intent": IntentCategory.RECOMMENDATION_QUERY, "expected_entities": {"crop": "Cotton"}},

    # 9. Yield/Production queries (5 queries)
    {"query": "How is wheat doing in Punjab?", "expected_intent": IntentCategory.YIELD_QUERY, "expected_entities": {"crop": "Wheat", "state": "Punjab"}},
    {"query": "Production statistics for rice", "expected_intent": IntentCategory.YIELD_QUERY, "expected_entities": {"crop": "Rice"}},
    {"query": "Yield data for Maharashtra", "expected_intent": IntentCategory.YIELD_QUERY, "expected_entities": {"state": "Maharashtra"}},
    {"query": "Harvest output in Gujarat", "expected_intent": IntentCategory.YIELD_QUERY, "expected_entities": {"state": "Gujarat"}},
    {"query": "Crop performance in Karnataka", "expected_intent": IntentCategory.YIELD_QUERY, "expected_entities": {"state": "Karnataka"}},

    # 10. Filter queries (5 queries)
    {"query": "Show wheat in Punjab", "expected_intent": IntentCategory.FILTER, "expected_entities": {"crop": "Wheat", "state": "Punjab"}},
    {"query": "Filter by Coimbatore", "expected_intent": IntentCategory.FILTER, "expected_entities": {"district": "Coimbatore", "state": "Tamil Nadu"}},
    {"query": "Data for rice from 2023-01-01 to 2023-06-01", "expected_intent": IntentCategory.FILTER, "expected_entities": {"crop": "Rice"}},
    {"query": "Reset filters", "expected_intent": IntentCategory.RESET, "expected_entities": {}},
    {"query": "All crops in Rajasthan", "expected_intent": IntentCategory.FILTER, "expected_entities": {"state": "Rajasthan"}},

    # 11. Help queries (3 queries)
    {"query": "Help", "expected_intent": IntentCategory.HELP, "expected_entities": {}},
    {"query": "What can you do?", "expected_intent": IntentCategory.HELP, "expected_entities": {}},
    {"query": "How to use this system?", "expected_intent": IntentCategory.HELP, "expected_entities": {}},

    # 12. Unsupported queries (7 queries)
    {"query": "What is the stock price of wheat?", "expected_intent": IntentCategory.UNSUPPORTED, "expected_entities": {}},
    {"query": "Send an email to the farmer", "expected_intent": IntentCategory.UNSUPPORTED, "expected_entities": {}},
    {"query": "What is the cost of fertilizer?", "expected_intent": IntentCategory.UNSUPPORTED, "expected_entities": {}},
    {"query": "Government scheme for agriculture", "expected_intent": IntentCategory.UNSUPPORTED, "expected_entities": {}},
    {"query": "Best seed variety for cotton", "expected_intent": IntentCategory.UNSUPPORTED, "expected_entities": {}},
    {"query": "Pesticide recommendation for rice", "expected_intent": IntentCategory.UNSUPPORTED, "expected_entities": {}},
    {"query": "Crop insurance details", "expected_intent": IntentCategory.UNSUPPORTED, "expected_entities": {}},

    # 13. Ambiguous queries (5 queries)
    {"query": "Weather?", "expected_intent": IntentCategory.GENERAL_QUERY, "expected_entities": {}},
    {"query": "Tell me about rain", "expected_intent": IntentCategory.GENERAL_QUERY, "expected_entities": {}},
    {"query": "How is it going?", "expected_intent": IntentCategory.GENERAL_QUERY, "expected_entities": {}},
    {"query": "Data for Punjab", "expected_intent": IntentCategory.GENERAL_QUERY, "expected_entities": {"state": "Punjab"}},
    {"query": "Show me", "expected_intent": IntentCategory.GENERAL_QUERY, "expected_entities": {}},

    # 14. Different wording / paraphrases (5 queries)
    {"query": "Will precipitation occur tomorrow?", "expected_intent": IntentCategory.FORECAST, "expected_entities": {}},
    {"query": "How much rain is expected?", "expected_intent": IntentCategory.RAINFALL_QUERY, "expected_entities": {}},
    {"query": "Is there a chance of rain?", "expected_intent": IntentCategory.RAINFALL_QUERY, "expected_entities": {}},
    {"query": "What will the temperature be?", "expected_intent": IntentCategory.TEMPERATURE_QUERY, "expected_entities": {}},
    {"query": "Will there be strong wind?", "expected_intent": IntentCategory.WIND_QUERY, "expected_entities": {}},

    # 15. Long queries (3 queries)
    {"query": "Can you tell me what the temperature will be like tomorrow compared to today in the state of Punjab?", "expected_intent": IntentCategory.COMPARISON, "expected_entities": {"state": "Punjab"}},
    {"query": "I want to know if the rainfall is increasing or decreasing over the past month in Maharashtra", "expected_intent": IntentCategory.TREND_QUERY, "expected_entities": {"state": "Maharashtra"}},
    {"query": "What actions should I take for my wheat crop in Punjab given the current weather conditions?", "expected_intent": IntentCategory.RECOMMENDATION_QUERY, "expected_entities": {"crop": "Wheat", "state": "Punjab"}},

    # 16. Short queries (3 queries)
    {"query": "Rain?", "expected_intent": IntentCategory.RAINFALL_QUERY, "expected_entities": {}},
    {"query": "Temp?", "expected_intent": IntentCategory.TEMPERATURE_QUERY, "expected_entities": {}},
    {"query": "Help me", "expected_intent": IntentCategory.HELP, "expected_entities": {}},

    # 17. Multilingual / transliterated (5 queries)
    {"query": "Mausam ka haal kya hai?", "expected_intent": IntentCategory.CURRENT_CONDITIONS, "expected_entities": {}},
    {"query": "Kya kal barish hogi?", "expected_intent": IntentCategory.FORECAST, "expected_entities": {}},
    {"query": "Punjab mein temperature kya hai?", "expected_intent": IntentCategory.TEMPERATURE_QUERY, "expected_entities": {"state": "Punjab"}},
    {"query": "Gehun ke liye kya karana chahiye?", "expected_intent": IntentCategory.RECOMMENDATION_QUERY, "expected_entities": {}},
    {"query": "Madhya Pradesh mein rainfall kitna hai?", "expected_intent": IntentCategory.RAINFALL_QUERY, "expected_entities": {"state": "Madhya Pradesh"}},
]


class TestQueryUnderstandingEngine:
    def test_all_queries_parseable(self, engine: QueryUnderstandingEngine) -> None:
        for case in TEST_QUERIES:
            result = engine.parse(case["query"])
            assert result.intent is not None, f"Failed to parse: {case['query']}"

    def test_intent_accuracy(self, engine: QueryUnderstandingEngine) -> None:
        correct = 0
        for case in TEST_QUERIES:
            result = engine.parse(case["query"])
            if result.intent == case["expected_intent"]:
                correct += 1
        accuracy = correct / len(TEST_QUERIES)
        print(f"Intent accuracy: {correct}/{len(TEST_QUERIES)} = {accuracy:.2%}")
        assert accuracy >= 0.75, f"Intent accuracy {accuracy:.2%} below 75% threshold"

    def test_entity_extraction_accuracy(self, engine: QueryUnderstandingEngine) -> None:
        correct = 0
        total_entities = 0
        for case in TEST_QUERIES:
            result = engine.parse(case["query"])
            for key, value in case.get("expected_entities", {}).items():
                total_entities += 1
                if result.entities.get(key) == value:
                    correct += 1
        if total_entities > 0:
            accuracy = correct / total_entities
            print(f"Entity accuracy: {correct}/{total_entities} = {accuracy:.2%}")
            assert accuracy >= 0.70, f"Entity accuracy {accuracy:.2%} below 70% threshold"

    def test_unsupported_queries_detected(self, engine: QueryUnderstandingEngine) -> None:
        unsupported_cases = [c for c in TEST_QUERIES if c["expected_intent"] == IntentCategory.UNSUPPORTED]
        for case in unsupported_cases:
            result = engine.parse(case["query"])
            assert result.intent == IntentCategory.UNSUPPORTED, f"Expected UNSUPPORTED for: {case['query']}"
            assert result.unsupported_reason is not None

    def test_ambiguity_detection(self, engine: QueryUnderstandingEngine) -> None:
        ambiguous = ["Weather?", "Tell me about rain", "How is it going?", "Show me", "Data for Punjab"]
        for query in ambiguous:
            result = engine.parse(query)
            assert result.needs_clarification is True, f"Expected clarification for: {query}"
            assert len(result.clarification_options) > 0

    def test_help_intent(self, engine: QueryUnderstandingEngine) -> None:
        for query in ["Help", "What can you do?", "How to use this system?"]:
            result = engine.parse(query)
            assert result.intent == IntentCategory.HELP

    def test_comparison_detection(self, engine: QueryUnderstandingEngine) -> None:
        comparisons = [
            "Compare tomorrow with today",
            "Is tomorrow hotter than today?",
            "Compare rainfall this week vs last week",
        ]
        for query in comparisons:
            result = engine.parse(query)
            assert result.intent == IntentCategory.COMPARISON, f"Expected COMPARISON for: {query}"
            assert result.comparison is not None

    def test_relative_date_resolution(self, engine: QueryUnderstandingEngine) -> None:
        today = datetime.utcnow().date()
        test_cases = [
            ("today", today.isoformat()),
            ("tomorrow", (today + timedelta(days=1)).isoformat()),
            ("yesterday", (today - timedelta(days=1)).isoformat()),
        ]
        for relative, expected_date in test_cases:
            result = engine.parse(f"What will the weather be {relative}?")
            assert result.time_period.start == expected_date
            assert result.time_period.relative == relative

    def test_absolute_date_extraction(self, engine: QueryUnderstandingEngine) -> None:
        result = engine.parse("Weather data from 2023-01-01 to 2023-06-01")
        assert result.time_period.start == "2023-01-01"
        assert result.time_period.end == "2023-06-01"

    def test_metric_resolution(self, engine: QueryUnderstandingEngine) -> None:
        test_cases = [
            ("rainfall", "rainfall_mm"),
            ("temperature", "temperature_c"),
            ("humidity", "humidity_pct"),
            ("soil moisture", "soil_moisture_pct"),
            ("wind", "wind_speed_kmh"),
        ]
        for raw, canonical in test_cases:
            result = engine.parse(f"What is the {raw} in Punjab?")
            assert canonical in result.variables, f"Expected {canonical} in variables for: {raw}"

    def test_location_extraction(self, engine: QueryUnderstandingEngine) -> None:
        test_cases = [
            ("Punjab", "state"),
            ("Ludhiana", "district"),
            ("Karnataka", "state"),
            ("Bangalore", "district"),
        ]
        for location, expected_key in test_cases:
            result = engine.parse(f"{location} weather")
            assert expected_key in result.entities, f"Expected {expected_key} in entities for: {location}"
            assert result.entities[expected_key] == location

    def test_crop_extraction(self, engine: QueryUnderstandingEngine) -> None:
        for crop in ["Wheat", "Rice", "Cotton", "Maize"]:
            result = engine.parse(f"How is {crop} doing?")
            assert result.entities.get("crop") == crop

    def test_confidence_scoring(self, engine: QueryUnderstandingEngine) -> None:
        high_confidence = engine.parse("Will it rain tomorrow in Punjab?")
        assert high_confidence.confidence >= 0.7

        vague = engine.parse("Weather?")
        assert vague.confidence <= 0.5

    def test_language_detection(self, engine: QueryUnderstandingEngine) -> None:
        result = engine.parse("Mausam ka haal kya hai?")
        assert result.language == "hi"

        result = engine.parse("What is the weather?")
        assert result.language == "en"

    def test_empty_query(self, engine: QueryUnderstandingEngine) -> None:
        result = engine.parse("")
        assert result.intent == IntentCategory.UNSUPPORTED
        assert result.unsupported_reason == "Empty query"

    def test_structured_query_schema(self, engine: QueryUnderstandingEngine) -> None:
        result = engine.parse("Will it rain tomorrow in Punjab?")
        assert result.intent is not None
        assert isinstance(result.entities, dict)
        assert isinstance(result.time_period, TimePeriod)
        assert isinstance(result.variables, list)
        assert isinstance(result.comparison, (type(None), ComparisonSpec))
        assert 0.0 <= result.confidence <= 1.0
        assert isinstance(result.needs_clarification, bool)
        assert isinstance(result.clarification_options, list)
        assert isinstance(result.ambiguity_reasons, list)
        assert result.raw_query == "Will it rain tomorrow in Punjab?"

    def test_context_backfill(self, engine: QueryUnderstandingEngine) -> None:
        context = {"last_state": "Punjab", "last_crop": "Wheat", "last_metric": "rainfall"}
        result = engine.parse("What about yesterday?", context=context)
        assert result.entities.get("state") == "Punjab"
        assert result.entities.get("crop") == "Wheat"
        assert result.entities.get("metric") == "rainfall"
        assert result.time_period.relative == "yesterday"
