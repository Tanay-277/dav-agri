from __future__ import annotations

from typing import Any

import pandas as pd

from analytics.engine import (
    analyze_current_conditions,
    analyze_rainfall_trends,
    analyze_temperature_trends,
    check_thresholds,
    compare_time_periods,
    compute_kpis,
    detect_anomalies,
    generate_insights,
)
from database import data
from models.schemas import DashboardFilters
from nlu.schema import IntentCategory, StructuredQuery


class QueryExecutor:
    """Execute a StructuredQuery against the deterministic analytics engine."""

    def execute(self, query: StructuredQuery) -> dict[str, Any]:
        """Execute the structured query and return results."""
        if query.unsupported_reason:
            return {
                "success": False,
                "error": query.unsupported_reason,
                "intent": query.intent,
                "confidence": query.confidence,
            }

        if query.needs_clarification:
            return {
                "success": False,
                "needs_clarification": True,
                "clarification_options": query.clarification_options,
                "ambiguity_reasons": query.ambiguity_reasons,
                "intent": query.intent,
                "confidence": query.confidence,
            }

        # Handle UI control intents
        ui_intents = {
            IntentCategory.RESET: {"message": "Filters cleared.", "action": "reset"},
            IntentCategory.READ_ALOUD: {"message": "Reading current insights aloud.", "action": "read_aloud"},
            IntentCategory.STOP: {"message": "Stopping.", "action": "stop"},
            IntentCategory.PAUSE: {"message": "Paused.", "action": "pause"},
            IntentCategory.RESUME: {"message": "Resumed.", "action": "resume"},
            IntentCategory.HELP: {"message": "You can ask about weather, forecasts, trends, comparisons, and recommendations.", "action": "help"},
        }
        if query.intent in ui_intents:
            return {
                "success": True,
                "intent": query.intent,
                "data": [],
                "message": ui_intents[query.intent]["message"],
                "action": ui_intents[query.intent].get("action"),
                "confidence": query.confidence,
            }

        # Convert structured query to filters
        filters = self._to_filters(query)
        df = data.get_filtered(filters)

        if df.empty:
            return {
                "success": True,
                "intent": query.intent,
                "data": None,
                "message": "No data found for the specified criteria.",
                "confidence": query.confidence,
            }

        # Route to appropriate analytics function
        result = self._route(query, df)
        result["success"] = True
        result["intent"] = query.intent
        result["confidence"] = query.confidence
        result["filters"] = filters
        result["row_count"] = int(len(df))
        return result

    def _to_filters(self, query: StructuredQuery) -> dict[str, Any]:
        """Convert StructuredQuery entities to DashboardFilters dict."""
        entities = query.entities
        filters: dict[str, Any] = {}

        if "crop" in entities:
            filters["crop"] = entities["crop"]
        if "state" in entities:
            filters["state"] = entities["state"]
        if "district" in entities:
            filters["district"] = entities["district"]

        tp = query.time_period
        if tp.start:
            filters["start_date"] = tp.start
        if tp.end:
            filters["end_date"] = tp.end

        return filters

    def _route(self, query: StructuredQuery, df: pd.DataFrame) -> dict[str, Any]:
        """Route query to the appropriate analytics function."""
        intent = IntentCategory(query.intent)

        if intent == IntentCategory.CURRENT_CONDITIONS:
            return self._handle_current_conditions(query, df)
        if intent == IntentCategory.FORECAST:
            return self._handle_forecast(query, df)
        if intent == IntentCategory.TEMPERATURE_QUERY:
            return self._handle_metric_query(query, df, "temperature_c", "Temperature")
        if intent == IntentCategory.RAINFALL_QUERY:
            return self._handle_metric_query(query, df, "rainfall_mm", "Rainfall")
        if intent == IntentCategory.WIND_QUERY:
            return self._handle_metric_query(query, df, "wind_speed_kmh", "Wind Speed")
        if intent == IntentCategory.HUMIDITY_QUERY:
            return self._handle_metric_query(query, df, "humidity_pct", "Humidity")
        if intent == IntentCategory.SOIL_QUERY:
            return self._handle_metric_query(query, df, "soil_moisture_pct", "Soil Moisture")
        if intent == IntentCategory.YIELD_QUERY:
            return self._handle_yield_query(query, df)
        if intent == IntentCategory.COMPARISON:
            return self._handle_comparison(query, df)
        if intent == IntentCategory.TREND_QUERY:
            return self._handle_trend_query(query, df)
        if intent == IntentCategory.HISTORICAL_QUERY:
            return self._handle_historical(query, df)
        if intent == IntentCategory.RECOMMENDATION_QUERY:
            return self._handle_recommendation(query, df)
        if intent == IntentCategory.THRESHOLD_QUERY:
            return self._handle_threshold(query, df)
        if intent == IntentCategory.ANOMALY_QUERY:
            return self._handle_anomaly(query, df)
        if intent == IntentCategory.GENERAL_QUERY:
            return self._handle_general(query, df)
        if intent == IntentCategory.FILTER:
            return self._handle_filter(query, df)

        # Default: generate insights
        return self._handle_general(query, df)

    def _handle_current_conditions(self, query: StructuredQuery, df: pd.DataFrame) -> dict[str, Any]:
        location_id = query.entities.get("state", "")
        if query.entities.get("district"):
            location_id = f"{query.entities['state']}_{query.entities['district']}"
        insights = analyze_current_conditions(df, location_id=location_id)
        return {
            "data": [i.model_dump() for i in insights],
            "message": " | ".join(i.message for i in insights) if insights else "No current conditions data available.",
        }

    def _handle_forecast(self, query: StructuredQuery, df: pd.DataFrame) -> dict[str, Any]:
        location_id = query.entities.get("state", "")
        if query.entities.get("district"):
            location_id = f"{query.entities['state']}_{query.entities['district']}"
        insights = analyze_current_conditions(df, location_id=location_id)
        kpis = compute_kpis(df)
        return {
            "data": [i.model_dump() for i in insights],
            "kpis": [k.model_dump() for k in kpis],
            "message": "Forecast data is not yet available in MVP. Showing current conditions instead.",
        }

    def _handle_metric_query(
        self, query: StructuredQuery, df: pd.DataFrame, metric: str, label: str
    ) -> dict[str, Any]:
        insights = analyze_current_conditions(df, location_id=query.entities.get("state"))
        relevant = [i for i in insights if metric in (i.metric or "")]
        kpis = compute_kpis(df)
        message = f"Current {label}: {relevant[0].message.split(' is ')[1]}" if relevant else f"No {label.lower()} data available."
        return {
            "data": [i.model_dump() for i in relevant],
            "kpis": [k.model_dump() for k in kpis],
            "message": message,
        }

    def _handle_yield_query(self, query: StructuredQuery, df: pd.DataFrame) -> dict[str, Any]:
        crop = query.entities.get("crop")
        if crop:
            df = df[df["crop"] == crop] if "crop" in df.columns else df
        kpis = compute_kpis(df)
        insights = generate_insights(df, location_id=query.entities.get("state"))
        return {
            "data": [i.model_dump() for i in insights],
            "kpis": [k.model_dump() for k in kpis],
            "message": f"Yield analysis for {crop or 'all crops'}.",
        }

    def _handle_comparison(self, query: StructuredQuery, df: pd.DataFrame) -> dict[str, Any]:
        tp = query.time_period
        if tp.start and tp.end:
            insights = generate_insights(df, location_id=query.entities.get("state"))
            kpis = compute_kpis(df)
            return {
                "data": [i.model_dump() for i in insights],
                "kpis": [k.model_dump() for k in kpis],
                "message": "Period comparison analysis.",
            }

        insights = analyze_current_conditions(df, location_id=query.entities.get("state"))
        kpis = compute_kpis(df)
        return {
            "data": [i.model_dump() for i in insights],
            "kpis": [k.model_dump() for k in kpis],
            "message": "Comparison analysis. Specify two time periods for detailed comparison.",
        }

    def _handle_trend_query(self, query: StructuredQuery, df: pd.DataFrame) -> dict[str, Any]:
        insights = generate_insights(df, location_id=query.entities.get("state"))
        trends = [i for i in insights if i.type == "trend"]
        return {
            "data": [i.model_dump() for i in insights],
            "message": " | ".join(i.message for i in trends) if trends else "No significant trends detected.",
        }

    def _handle_historical(self, query: StructuredQuery, df: pd.DataFrame) -> dict[str, Any]:
        insights = analyze_current_conditions(df, location_id=query.entities.get("state"))
        kpis = compute_kpis(df)
        return {
            "data": [i.model_dump() for i in insights],
            "kpis": [k.model_dump() for k in kpis],
            "message": f"Historical data for {query.time_period.relative or 'the specified period'}.",
        }

    def _handle_recommendation(self, query: StructuredQuery, df: pd.DataFrame) -> dict[str, Any]:
        from recommendations.engine import generate_recommendations
        recs = generate_recommendations(df)
        insights = generate_insights(df, location_id=query.entities.get("state"))
        return {
            "data": [i.model_dump() for i in insights],
            "recommendations": [r.model_dump() for r in recs],
            "message": " | ".join(r.message for r in recs),
        }

    def _handle_threshold(self, query: StructuredQuery, df: pd.DataFrame) -> dict[str, Any]:
        insights = check_thresholds(df)
        return {
            "data": [i.model_dump() for i in insights],
            "message": " | ".join(i.message for i in insights) if insights else "All metrics within normal thresholds.",
        }

    def _handle_anomaly(self, query: StructuredQuery, df: pd.DataFrame) -> dict[str, Any]:
        insights = detect_anomalies(df)
        return {
            "data": [i.model_dump() for i in insights],
            "message": " | ".join(i.message for i in insights) if insights else "No anomalies detected.",
        }

    def _handle_general(self, query: StructuredQuery, df: pd.DataFrame) -> dict[str, Any]:
        insights = generate_insights(df, location_id=query.entities.get("state"))
        kpis = compute_kpis(df)
        return {
            "data": [i.model_dump() for i in insights],
            "kpis": [k.model_dump() for k in kpis],
            "message": "General analysis complete.",
        }

    def _handle_filter(self, query: StructuredQuery, df: pd.DataFrame) -> dict[str, Any]:
        kpis = compute_kpis(df)
        insights = generate_insights(df, location_id=query.entities.get("state"))
        return {
            "data": [i.model_dump() for i in insights],
            "kpis": [k.model_dump() for k in kpis],
            "message": f"Showing data for {', '.join(f'{k}={v}' for k, v in query.entities.items())}.",
        }
