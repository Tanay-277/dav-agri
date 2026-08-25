from __future__ import annotations

import logging
from typing import Any

from text_to_speech.languages import get_language_config, is_language_supported
from text_to_speech.normalizer import normalize_for_tts, normalize_number, normalize_unit
from text_to_speech.provider import get_tts_provider
from text_to_speech.schemas import (
    InsightType,
    LocalizedResponse,
    SynthesisRequest,
    SynthesisResponse,
    VoiceGender,
)
from text_to_speech.templates import (
    TEMPERATURE_FEELING,
    TREND_DIRECTION,
    WARNING_TEMPLATES,
    get_template,
)

logger = logging.getLogger(__name__)


class TextToSpeechEngine:
    """High-level engine that converts structured insights to localized speech.

    Pipeline:
    1. Structured insight → Human-readable response (templates)
    2. Human-readable response → Localized response (number/unit normalization)
    3. Localized response → Speech synthesis (TTS provider)
    """

    def __init__(self, provider_name: str | None = None) -> None:
        self.provider_name = provider_name
        try:
            self._provider = get_tts_provider(provider_name)
        except RuntimeError:
            from text_to_speech.provider import MockTTSProvider, register_tts_provider
            register_tts_provider(MockTTSProvider())
            self._provider = get_tts_provider(provider_name)

    def generate_response(self, insight: dict[str, Any], language: str = "en") -> LocalizedResponse:
        """Convert a structured insight dict to a localized text response.

        The insight dict is expected to have keys like:
        - type: InsightType
        - message: str
        - metric: str
        - location: str
        - value: float
        - values: dict
        - confidence: float
        """
        if not is_language_supported(language):
            language = "en"

        insight_type = insight.get("type", InsightType.CURRENT_WEATHER)
        if isinstance(insight_type, str):
            try:
                insight_type = InsightType(insight_type)
            except ValueError:
                insight_type = InsightType.CURRENT_WEATHER

        template = get_template(insight_type, language)
        if not template:
            template = get_template(InsightType.CURRENT_WEATHER, language) or get_template(InsightType.CURRENT_WEATHER, "en")

        text = self._fill_template(template, insight, language)
        text = normalize_for_tts(text, language=language)

        return LocalizedResponse(
            text=text,
            language=language,
            insight_type=insight_type,
            original_values=self._extract_values(insight),
        )

    async def synthesize_response(
        self,
        insight: dict[str, Any],
        language: str = "en",
        voice_gender: VoiceGender = VoiceGender.FEMALE,
        rate: float = 1.0,
    ) -> SynthesisResponse:
        """End-to-end: structured insight → audio."""
        localized = self.generate_response(insight, language)
        request = SynthesisRequest(
            text=localized.text,
            language=localized.language,
            voice_gender=voice_gender,
            rate=rate,
        )
        response = await self._provider.synthesize(request)
        if response.success:
            response.metadata = {
                **(response.metadata or {}),
                "insight_type": localized.insight_type.value,
                "original_values": localized.original_values,
            }
        return response

    def _fill_template(self, template: str, insight: dict[str, Any], language: str) -> str:
        result = insight.get("result", {})
        values = insight.get("values", {})
        metric = insight.get("metric", "")
        if not metric and result.get("metric"):
            metric = result["metric"]

        def _val(key: str, default: float = 0) -> float:
            if key in insight:
                return insight[key]
            if key in values:
                return values[key]
            if key in result:
                return result[key]
            return default

        location = insight.get("location", "")
        if not location:
            location = result.get("location", "")
        if not location:
            location = values.get("location", "")

        filled = {
            "location": location,
            "location_a": insight.get("location_a", location),
            "location_b": insight.get("location_b", ""),
            "metric": self._localize_metric(metric, language),
            "temperature": normalize_number(_val("temperature", _val("value", 0)), language),
            "temperature_min": normalize_number(_val("temperature_min", _val("min", 0)), language),
            "temperature_max": normalize_number(_val("temperature_max", _val("max", 0)), language),
            "rain_probability": normalize_number(_val("rain_probability", 0), language),
            "rainfall": normalize_number(_val("rainfall", 0), language),
            "yield_value": normalize_number(_val("yield", _val("yield_value", 0)), language),
            "moisture_value": normalize_number(_val("moisture", _val("moisture_value", 0)), language),
            "crop": insight.get("crop", ""),
            "value_a": normalize_number(_val("value_a", 0), language),
            "value_b": normalize_number(_val("value_b", 0), language),
            "difference": normalize_number(_val("difference", _val("magnitude", 0)), language),
            "direction": self._localize_direction(insight.get("direction", "stable"), language),
            "magnitude": normalize_number(_val("magnitude", 0), language),
            "period": insight.get("period", ""),
            "message": insight.get("message", ""),
            "action": insight.get("action", ""),
            "reason": insight.get("reason", ""),
            "question": insight.get("question", ""),
            "options": insight.get("options", ""),
            "comparison": insight.get("comparison", ""),
            "status": insight.get("status", ""),
            "temperature_feeling": self._localize_feeling(insight.get("temperature_feeling", "normal"), language),
        }
        try:
            return template.format(**filled)
        except KeyError as exc:
            logger.warning("Missing template key: %s", exc)
            return template

    def _localize_metric(self, metric: str, language: str) -> str:
        metric_map = {
            "rainfall_mm": {"en": "rainfall", "hi": "barish", "ta": "mazhai", "te": "varsham", "kn": "male", "mr": "paus", "bn": "baris"},
            "temperature_c": {"en": "temperature", "hi": "temperature", "ta": "nilam", "te": "nilam", "kn": "nilam", "mr": "temperature", "bn": "tap"},
            "humidity_pct": {"en": "humidity", "hi": "nam", "ta": "namam", "te": "namam", "kn": "nam", "mr": "nam", "bn": "nam"},
            "soil_moisture_pct": {"en": "soil moisture", "hi": "mitti mein paani", "ta": "man nilam", "te": "manam nilam", "kn": "bhoomi niraya", "mr": "matitil paani", "bn": "matir pani"},
            "yield_kg_per_ha": {"en": "yield", "hi": "utpatti", "ta": "varavu", "te": "samputo", "kn": "output", "mr": "utpanna", "bn": "fal"},
        }
        return metric_map.get(metric, {}).get(language, metric)

    def _localize_direction(self, direction: str, language: str) -> str:
        return TREND_DIRECTION.get(language, TREND_DIRECTION["en"]).get(direction, direction)

    def _localize_feeling(self, feeling: str, language: str) -> str:
        return TEMPERATURE_FEELING.get(language, TEMPERATURE_FEELING["en"]).get(feeling, feeling)

    def _extract_values(self, insight: dict[str, Any]) -> dict[str, Any]:
        values = {}
        for key in ["value", "values", "location", "location_a", "location_b", "metric", "crop", "direction", "period", "message", "action", "reason", "comparison", "status"]:
            if key in insight:
                values[key] = insight[key]
        return values
