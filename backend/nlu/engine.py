from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Any

from nlu.schema import ComparisonSpec, IntentCategory, StructuredQuery, TimePeriod
from nlu.vocabularies import (
    COMPARISON_PHRASES,
    CROPS,
    DISTRICTS,
    HISTORICAL_QUERY,
    INTENT_TRIGGERS,
    LANGUAGE_KEYWORDS,
    METRIC_ALIASES,
    METRIC_DISPLAY_NAMES,
    RELATIVE_DATE_PATTERNS,
    STATES,
    THRESHOLDS,
    UNSUPPORTED_INDICATORS,
)


class QueryUnderstandingEngine:
    """Convert natural-language queries into structured query representations."""

    def __init__(self) -> None:
        self._compiled_date_patterns = {
            re.compile(pattern, re.IGNORECASE): meaning
            for pattern, meaning in RELATIVE_DATE_PATTERNS.items()
        }

    def parse(self, query: str, context: dict[str, Any] | None = None) -> StructuredQuery:
        """Parse a natural-language query into a StructuredQuery."""
        context = context or {}
        raw = query.strip()
        if not raw:
            return self._empty_result(raw)

        lower = raw.lower()
        tokens = [re.sub(r"[^a-zA-Z0-9]", "", t).lower() for t in raw.split()]

        unsupported_reason = self._detect_unsupported(lower)
        if unsupported_reason:
            return StructuredQuery(
                intent=IntentCategory.UNSUPPORTED,
                raw_query=raw,
                confidence=0.9,
                unsupported_reason=unsupported_reason,
                needs_clarification=False,
                clarification_options=[],
            )

        intent, intent_confidence = self._classify_intent(lower, tokens, raw)

        entities = self._extract_entities(raw, lower, tokens, context)
        time_period = self._interpret_time(raw, lower, context)
        variables = self._resolve_metrics(entities.get("metric"), intent)
        comparison = self._detect_comparison(lower, entities, time_period, intent)

        ambiguity_reasons, clarification_options = self._detect_ambiguity(
            intent, entities, time_period, variables
        )
        needs_clarification = len(ambiguity_reasons) > 0

        output_type = self._infer_output_type(intent, comparison)
        language = self._detect_language(raw, lower)

        confidence = min(intent_confidence, 1.0)
        if needs_clarification:
            confidence = min(confidence, 0.6)

        return StructuredQuery(
            intent=intent,
            entities=entities,
            time_period=time_period,
            variables=variables,
            comparison=comparison,
            aggregation=None,
            units=None,
            language=language,
            output_type=output_type,
            confidence=round(confidence, 2),
            needs_clarification=needs_clarification,
            clarification_options=clarification_options,
            raw_query=raw,
            ambiguity_reasons=ambiguity_reasons,
            unsupported_reason=None,
        )

    def _classify_intent(self, lower: str, tokens: list[str], raw: str) -> tuple[IntentCategory, float]:
        scores: dict[IntentCategory, float] = {}

        for intent_str, triggers in INTENT_TRIGGERS.items():
            try:
                intent = IntentCategory(intent_str)
            except ValueError:
                continue
            score = 0.0
            for trigger in triggers:
                if trigger in lower:
                    if " " not in trigger and trigger not in tokens:
                        continue
                    score += len(trigger.split()) * 0.2
                    if trigger in tokens:
                        score += 0.3
            if score > 0:
                scores[intent] = score

        for phrase in COMPARISON_PHRASES:
            if phrase in lower:
                scores[IntentCategory.COMPARISON] = scores.get(IntentCategory.COMPARISON, 0.0) + 0.5
                break

        if "will it" in lower or "going to" in lower:
            scores[IntentCategory.FORECAST] = scores.get(IntentCategory.FORECAST, 0.0) + 0.4
            scores[IntentCategory.CURRENT_CONDITIONS] = scores.get(IntentCategory.CURRENT_CONDITIONS, 0.0) + 0.2

        if lower.startswith("is it") or lower.startswith("is there"):
            scores[IntentCategory.CURRENT_CONDITIONS] = scores.get(IntentCategory.CURRENT_CONDITIONS, 0.0) + 0.3
            scores[IntentCategory.THRESHOLD_QUERY] = scores.get(IntentCategory.THRESHOLD_QUERY, 0.0) + 0.2

        if lower.startswith("how") or "how much" in lower or "how is" in lower:
            scores[IntentCategory.GENERAL_QUERY] = scores.get(IntentCategory.GENERAL_QUERY, 0.0) + 0.3

        if "crop" in lower or any(c.lower() in lower for c in CROPS):
            scores[IntentCategory.YIELD_QUERY] = scores.get(IntentCategory.YIELD_QUERY, 0.0) + 0.5

        for phrase in ["too hot", "too cold", "too dry", "too wet"]:
            if phrase in lower:
                scores[IntentCategory.THRESHOLD_QUERY] = scores.get(IntentCategory.THRESHOLD_QUERY, 0.0) + 0.6
                break

        for phrase in ["above", "below", "threshold"]:
            if phrase in lower:
                scores[IntentCategory.THRESHOLD_QUERY] = scores.get(IntentCategory.THRESHOLD_QUERY, 0.0) + 0.5
                break

        for phrase in ["going up", "going down", "rising", "falling"]:
            if phrase in lower:
                scores[IntentCategory.TREND_QUERY] = scores.get(IntentCategory.TREND_QUERY, 0.0) + 0.5
                break

        for phrase in ["what actions should i take", "advice", "action", "should i"]:
            if phrase in lower:
                scores[IntentCategory.RECOMMENDATION_QUERY] = scores.get(IntentCategory.RECOMMENDATION_QUERY, 0.0) + 0.5
                break

        for phrase in ["tell me about", "tell me"]:
            if phrase in lower:
                scores[IntentCategory.GENERAL_QUERY] = scores.get(IntentCategory.GENERAL_QUERY, 0.0) + 0.6
                break

        if not scores or max(scores.values()) == 0:
            return IntentCategory.GENERAL_QUERY, 0.4

        best_intent = max(scores, key=scores.get)
        best_score = scores[best_intent]

        if best_intent == IntentCategory.FILTER:
            specific_starts = ["show", "filter", "display", "get", "find"]
            if any(lower.startswith(s) for s in specific_starts):
                stripped = raw.strip().lower()
                if stripped in ("show me", "show", "display", "get", "find"):
                    best_intent = IntentCategory.GENERAL_QUERY
                    best_score = 0.4
                else:
                    best_score = max(best_score, 0.6)
            elif "data for" in lower:
                has_crop = any(c.lower() in lower for c in CROPS)
                has_metric = any(m.lower() in lower for m in METRIC_ALIASES)
                if not has_crop and not has_metric:
                    best_intent = IntentCategory.GENERAL_QUERY
                    best_score = 0.4

        if best_intent == IntentCategory.CURRENT_CONDITIONS:
            for phrase in ["too hot", "too cold", "above", "below", "threshold", "is it dry", "is it wet"]:
                if phrase in lower:
                    best_intent = IntentCategory.THRESHOLD_QUERY
                    best_score = max(best_score, 0.7)
                    break

        if best_intent in (
            IntentCategory.TEMPERATURE_QUERY,
            IntentCategory.RAINFALL_QUERY,
            IntentCategory.WIND_QUERY,
            IntentCategory.HUMIDITY_QUERY,
            IntentCategory.SOIL_QUERY,
        ):
            for phrase in ["increasing", "decreasing", "going up", "going down", "rising", "falling"]:
                if phrase in lower:
                    best_intent = IntentCategory.TREND_QUERY
                    best_score = max(best_score, 0.7)
                    break

        if best_intent in (IntentCategory.TEMPERATURE_QUERY, IntentCategory.RAINFALL_QUERY):
            for phrase in ["outlier", "abnormal", "unusual", "anomaly"]:
                if phrase in lower:
                    best_intent = IntentCategory.ANOMALY_QUERY
                    best_score = max(best_score, 0.7)
                    break

        if best_intent == IntentCategory.GENERAL_QUERY:
            if any(c.lower() in lower for c in CROPS) and ("doing" in lower or "performance" in lower):
                best_intent = IntentCategory.YIELD_QUERY
                best_score = max(best_score, 0.6)

        confidence = min(best_score, 1.0)
        if best_score >= 0.5:
            confidence = max(confidence, 0.7)
        elif best_score >= 0.2:
            confidence = max(confidence, 0.5)

        return best_intent, round(confidence, 2)

    def _extract_entities(
        self, raw: str, lower: str, tokens: list[str], context: dict[str, Any]
    ) -> dict[str, Any]:
        entities: dict[str, Any] = {}

        crop = self._match_token(tokens, CROPS)
        if crop:
            entities["crop"] = crop

        state = self._match_token(tokens, STATES)
        if state:
            entities["state"] = state

        district_candidates = list(DISTRICTS.get(state, [])) if state else []
        if not district_candidates:
            for districts in DISTRICTS.values():
                district_candidates.extend(districts)
        district = self._match_token(tokens, district_candidates)
        if district:
            entities["district"] = district

        metric = self._match_token(tokens, list(METRIC_ALIASES.keys()))
        if metric:
            entities["metric"] = metric

        if "crop" not in entities and context.get("last_crop"):
            entities["crop"] = context["last_crop"]
        if "state" not in entities and context.get("last_state"):
            entities["state"] = context["last_state"]
        if "district" not in entities and context.get("last_district"):
            entities["district"] = context["last_district"]
        if "metric" not in entities and context.get("last_metric"):
            entities["metric"] = context["last_metric"]

        return entities

    def _interpret_time(
        self, raw: str, lower: str, context: dict[str, Any]
    ) -> TimePeriod:
        time_period = TimePeriod()

        for pattern, meaning in self._compiled_date_patterns.items():
            if pattern.search(lower):
                time_period.relative = meaning
                resolved = self._resolve_relative_date(meaning)
                if resolved:
                    time_period.start = resolved
                    time_period.end = resolved
                    time_period.is_historical = meaning in ("yesterday", "last_week", "last_month")
                    time_period.is_future = meaning in ("tomorrow", "next_week", "next_month")
                break

        date_matches = re.findall(r"\d{4}-\d{2}-\d{2}", raw)
        if date_matches:
            if len(date_matches) >= 2:
                time_period.start = date_matches[0]
                time_period.end = date_matches[1]
            elif len(date_matches) == 1:
                time_period.start = date_matches[0]
                time_period.end = date_matches[0]

        if not time_period.start and context.get("last_date_range"):
            time_period.start = context["last_date_range"].get("start")
            time_period.end = context["last_date_range"].get("end")

        return time_period

    def _resolve_relative_date(self, meaning: str) -> str | None:
        today = datetime.utcnow().date()
        if meaning == "today":
            return today.isoformat()
        if meaning == "tomorrow":
            return (today + timedelta(days=1)).isoformat()
        if meaning == "yesterday":
            return (today - timedelta(days=1)).isoformat()
        if meaning == "next_week":
            start = today + timedelta(days=7 - today.weekday())
            return start.isoformat()
        if meaning == "last_week":
            start = today - timedelta(days=today.weekday() + 7)
            return start.isoformat()
        if meaning == "next_month":
            if today.month == 12:
                start = today.replace(year=today.year + 1, month=1, day=1)
            else:
                start = today.replace(month=today.month + 1, day=1)
            return start.isoformat()
        if meaning == "last_month":
            if today.month == 1:
                start = today.replace(year=today.year - 1, month=12, day=1)
            else:
                start = today.replace(month=today.month - 1, day=1)
            return start.isoformat()
        return None

    def _resolve_metrics(self, raw_metric: str | None, intent: IntentCategory) -> list[str]:
        if not raw_metric:
            return []

        canonical = METRIC_ALIASES.get(raw_metric.lower())
        if canonical:
            return [canonical]

        intent_metric_map = {
            IntentCategory.TEMPERATURE_QUERY: ["temperature_c"],
            IntentCategory.RAINFALL_QUERY: ["rainfall_mm"],
            IntentCategory.WIND_QUERY: ["wind_speed_kmh"],
            IntentCategory.HUMIDITY_QUERY: ["humidity_pct"],
            IntentCategory.SOIL_QUERY: ["soil_moisture_pct"],
            IntentCategory.YIELD_QUERY: ["yield_kg_per_ha", "production_tonnes"],
        }
        return intent_metric_map.get(intent, [])

    def _detect_comparison(
        self, lower: str, entities: dict[str, Any], time_period: TimePeriod, intent: IntentCategory
    ) -> ComparisonSpec | None:
        if intent != IntentCategory.COMPARISON:
            return None

        comparison = ComparisonSpec()

        if time_period.relative and ("tomorrow" in (time_period.relative or "") or "yesterday" in (time_period.relative or "")):
            comparison.type = "time"
            comparison.entities = [time_period.relative or ""]
        elif "vs" in lower or "versus" in lower or "compare" in lower:
            comparison.type = "time"
            comparison.entities = ["period1", "period2"]
        else:
            comparison.type = "metric"
            comparison.entities = list(entities.values())

        comparison.metric = entities.get("metric")
        return comparison

    def _detect_ambiguity(
        self,
        intent: IntentCategory,
        entities: dict[str, Any],
        time_period: TimePeriod,
        variables: list[str],
    ) -> tuple[list[str], list[str]]:
        reasons: list[str] = []
        options: list[str] = []

        ui_intents = {
            IntentCategory.RESET, IntentCategory.READ_ALOUD, IntentCategory.STOP,
            IntentCategory.PAUSE, IntentCategory.RESUME, IntentCategory.HELP,
            IntentCategory.UNSUPPORTED,
        }
        if intent not in ui_intents and not any(k in entities for k in ("crop", "state", "district")):
            reasons.append("No location specified")
            options = [f"{c} in {s}" for s in STATES[:3] for c in CROPS[:2]]
            options = options[:6]

        if intent in (
            IntentCategory.TEMPERATURE_QUERY,
            IntentCategory.RAINFALL_QUERY,
            IntentCategory.WIND_QUERY,
            IntentCategory.HUMIDITY_QUERY,
            IntentCategory.SOIL_QUERY,
            IntentCategory.YIELD_QUERY,
            IntentCategory.GENERAL_QUERY,
            IntentCategory.CURRENT_CONDITIONS,
            IntentCategory.THRESHOLD_QUERY,
            IntentCategory.ANOMALY_QUERY,
            IntentCategory.TREND_QUERY,
            IntentCategory.FILTER,
        ) and not variables:
            reasons.append("No metric specified")
            options = [
                METRIC_DISPLAY_NAMES[m]
                for m in ["rainfall_mm", "temperature_c", "humidity_pct", "soil_moisture_pct"]
            ]

        if intent in (
            IntentCategory.FORECAST,
            IntentCategory.HISTORICAL_QUERY,
            IntentCategory.TREND_QUERY,
            IntentCategory.COMPARISON,
        ) and not time_period.start and not time_period.relative:
            reasons.append("No time period specified")
            options = ["Today", "Tomorrow", "Last week", "Last month"]

        if intent == IntentCategory.YIELD_QUERY and "crop" not in entities:
            reasons.append("No crop specified")
            options = list(CROPS[:6])

        return reasons, options[:6]

    def _detect_unsupported(self, lower: str) -> str | None:
        for indicator in UNSUPPORTED_INDICATORS:
            if indicator in lower:
                return f"Query contains unsupported topic: '{indicator}'"
        return None

    def _infer_output_type(self, intent: IntentCategory, comparison: ComparisonSpec | None) -> str:
        if comparison:
            return "comparison"
        if intent in (IntentCategory.RECOMMENDATION_QUERY,):
            return "recommendation"
        if intent in (IntentCategory.TREND_QUERY, IntentCategory.ANOMALY_QUERY):
            return "detailed"
        return "summary"

    def _detect_language(self, raw: str, lower: str) -> str | None:
        if re.search(r"[\u0900-\u097F]", raw):
            return "hi"
        if re.search(r"[\u0B80-\u0BFF]", raw):
            return "ta"
        if re.search(r"[\u0C00-\u0C7F]", raw):
            return "te"
        if re.search(r"[\u0C80-\u0CFF]", raw):
            return "kn"
        if re.search(r"[\u0980-\u09FF]", raw):
            return "bn"

        lower_words = {re.sub(r"[^a-zA-Z0-9]", "", w) for w in lower.split()}
        for lang, keywords in LANGUAGE_KEYWORDS.items():
            if any(kw in lower_words for kw in keywords):
                return lang
        return "en"

    def _match_token(self, tokens: list[str], candidates: list[str] | tuple[str, ...]) -> str | None:
        lower_tokens = {re.sub(r"[^a-zA-Z0-9]", "", t).lower() for t in tokens}
        for candidate in candidates:
            if candidate.lower() in lower_tokens:
                return candidate
        return None

    def _empty_result(self, raw: str) -> StructuredQuery:
        return StructuredQuery(
            intent=IntentCategory.UNSUPPORTED,
            raw_query=raw,
            confidence=0.0,
            needs_clarification=False,
            clarification_options=[],
            unsupported_reason="Empty query",
        )
