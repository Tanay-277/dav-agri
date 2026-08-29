from __future__ import annotations

import json
import sys
from unittest.mock import patch

import pytest

from text_to_speech.engine import TextToSpeechEngine
from text_to_speech.languages import (
    LANGUAGE_CODE_MAP,
    SUPPORTED_LANGUAGES,
    get_language_config,
    is_language_supported,
)
from text_to_speech.normalizer import (
    normalize_for_tts,
    normalize_number,
    normalize_unit,
)
from text_to_speech.provider import (
    EdgeTTSProvider,
    MockTTSProvider,
    _registry,
    get_tts_provider,
    register_tts_provider,
)
from text_to_speech.schemas import (
    InsightType,
    SynthesisRequest,
    VoiceGender,
)
from text_to_speech.templates import (
    TREND_DIRECTION,
    WARNING_TEMPLATES,
    get_template,
)

DATASET_PATH = None
try:
    import importlib.resources as pkg_resources

    from text_to_speech import dataset as dataset_mod
    DATASET_PATH = pkg_resources.files(dataset_mod).joinpath("test_dataset.json")
except Exception:
    DATASET_PATH = None

TEST_DATASET: dict[str, dict[str, list[str]]] = {}
if DATASET_PATH:
    try:
        with open(DATASET_PATH, "r", encoding="utf-8") as f:
            TEST_DATASET = json.load(f)
    except Exception:
        pass

if not TEST_DATASET:
    TEST_DATASET = {
        "en": {"phrases": ["rain", "temperature", "yield", "soil moisture", "fifty five millimeters", "thirty degrees"]},
        "hi": {"phrases": ["barish", "temperature", "utpatti", "mitti", "pachas millimeter"]},
    }


@pytest.fixture(autouse=True)
def _register_mock():
    register_tts_provider(MockTTSProvider())
    yield
    register_tts_provider(MockTTSProvider())


class TestLanguageConfig:
    def test_all_supported_languages_present(self):
        expected = {"en", "hi", "ta", "te", "kn", "mr", "bn"}
        assert set(SUPPORTED_LANGUAGES.keys()) == expected

    def test_is_language_supported(self):
        assert is_language_supported("en")
        assert is_language_supported("hi")
        assert not is_language_supported("fr")

    def test_language_code_map(self):
        assert LANGUAGE_CODE_MAP.get("english") == "en"
        assert LANGUAGE_CODE_MAP.get("hindi") == "hi"

    def test_get_language_config(self):
        config = get_language_config("en")
        assert config.name == "English"
        assert config.tts_voice_female is not None


class TestNormalizer:
    def test_normalize_number_integer(self):
        assert normalize_number(1234) == "1,234"

    def test_normalize_number_float(self):
        assert normalize_number(1234.5) == "1,234.50"

    def test_normalize_number_string(self):
        assert normalize_number("1234") == "1,234"

    def test_normalize_unit_rainfall(self):
        result = normalize_unit("rainfall_mm", 55.0)
        assert "55" in result
        assert "mm" in result or "millimeter" in result.lower()

    def test_normalize_unit_temperature(self):
        result = normalize_unit("temperature_c", 30.0)
        assert "30" in result
        assert "degree" in result.lower()

    def test_normalize_for_tts_expands_units(self):
        text = "Rainfall is 55 mm today."
        result = normalize_for_tts(text)
        assert "millimeters" in result.lower()
        assert "mm" not in result

    def test_normalize_for_tts_collapses_whitespace(self):
        result = normalize_for_tts("  hello   world  ")
        assert result == "hello world"


class TestTemplates:
    def test_all_insight_types_have_english_template(self):
        for insight_type in InsightType:
            template = get_template(insight_type, "en")
            assert template, f"Missing English template for {insight_type}"

    def test_all_insight_types_have_all_language_templates(self):
        for insight_type in InsightType:
            for lang in SUPPORTED_LANGUAGES:
                template = get_template(insight_type, lang)
                assert template, f"Missing {lang} template for {insight_type}"

    def test_templates_preserve_numerical_placeholders(self):
        template = get_template(InsightType.TEMPERATURE, "en")
        assert "{temperature}" in template

    def test_warning_templates_present(self):
        for lang in SUPPORTED_LANGUAGES:
            for key in WARNING_TEMPLATES:
                assert key in WARNING_TEMPLATES
                assert lang in WARNING_TEMPLATES[key], f"Missing {lang} warning for {key}"

    def test_trend_direction_translations(self):
        for lang in TREND_DIRECTION:
            assert "up" in TREND_DIRECTION[lang]
            assert "down" in TREND_DIRECTION[lang]


class TestMockProvider:
    @pytest.mark.asyncio
    async def test_empty_text_returns_error(self):
        provider = get_tts_provider("mock")
        response = await provider.synthesize(SynthesisRequest(text="", language="en"))
        assert response.success is False
        assert response.error is not None
        assert response.error.code == "empty_text"

    @pytest.mark.asyncio
    async def test_successful_synthesis(self):
        provider = get_tts_provider("mock")
        response = await provider.synthesize(
            SynthesisRequest(text="Hello world", language="en")
        )
        assert response.success is True
        assert response.audio_bytes is not None
        assert response.duration_ms > 0
        assert response.provider == "mock"

    @pytest.mark.asyncio
    async def test_unsupported_language_fallback(self):
        provider = get_tts_provider("mock")
        response = await provider.synthesize(
            SynthesisRequest(text="Hello", language="fr")
        )
        assert response.success is True
        assert response.metadata is not None
        assert response.metadata.get("language") == "en"

    @pytest.mark.asyncio
    async def test_multilingual_synthesis(self):
        provider = get_tts_provider("mock")
        for code in ["hi", "ta", "te", "kn", "mr", "bn"]:
            response = await provider.synthesize(
                SynthesisRequest(text="Test phrase", language=code)
            )
            assert response.success is True, f"Failed for {code}"
            assert response.metadata is not None
            assert response.metadata.get("language") == code

    @pytest.mark.asyncio
    async def test_voice_gender_resolution(self):
        provider = get_tts_provider("mock")
        response = await provider.synthesize(
            SynthesisRequest(text="Test", language="en", voice_gender=VoiceGender.MALE)
        )
        assert response.success is True
        assert response.metadata is not None
        assert response.metadata.get("voice") is not None


class TestEdgeTTSProvider:
    def test_import_fails_gracefully(self):
        provider = EdgeTTSProvider()
        assert provider.name == "edge"

    def test_supports_language_returns_false_without_dependency(self):
        with patch.dict(sys.modules, {"edge_tts": None}):
            provider = EdgeTTSProvider()
            assert provider.supports_language("en") is False

    @pytest.mark.asyncio
    async def test_real_provider_generates_audio_bytes(self):
        provider = EdgeTTSProvider()
        if not provider._available:
            pytest.skip("edge-tts is not installed")
        response = await provider.synthesize(
            SynthesisRequest(text="Hello world", language="en")
        )
        assert response.success is True
        assert response.audio_bytes is not None
        assert len(response.audio_bytes) > 100
        assert response.provider == "edge"
        assert response.content_type == "audio/mpeg"
        assert not response.audio_bytes.startswith(b"MOCK_AUDIO")
        assert response.metadata is not None
        assert response.metadata.get("simulated") is not True

    @pytest.mark.asyncio
    async def test_real_provider_multilingual(self):
        provider = EdgeTTSProvider()
        if not provider._available:
            pytest.skip("edge-tts is not installed")
        for code in ["hi", "en"]:
            response = await provider.synthesize(
                SynthesisRequest(text="Test phrase", language=code)
            )
            assert response.success is True, f"Failed for {code}"
            assert response.audio_bytes is not None
            assert len(response.audio_bytes) > 100
            assert response.provider == "edge"


class TestProviderRegistration:
    def test_registers_edge_when_configured_and_available(self):
        from unittest.mock import MagicMock

        from text_to_speech.api import _register_configured_providers

        _registry._providers.clear()
        mock_settings = MagicMock()
        mock_settings.TTS_PROVIDER = "edge"
        mock_settings.TTS_ALLOW_MOCK = False

        with patch("text_to_speech.api._settings", mock_settings):
            _register_configured_providers()

        assert "edge" in _registry.list_providers()
        assert "mock" not in _registry.list_providers()
        _registry._providers.clear()

    def test_registers_both_edge_and_mock_when_mock_allowed(self):
        from unittest.mock import MagicMock

        from text_to_speech.api import _register_configured_providers

        _registry._providers.clear()
        mock_settings = MagicMock()
        mock_settings.TTS_PROVIDER = "edge"
        mock_settings.TTS_ALLOW_MOCK = True

        with patch("text_to_speech.api._settings", mock_settings):
            _register_configured_providers()

        assert "edge" in _registry.list_providers()
        assert "mock" in _registry.list_providers()
        _registry._providers.clear()

    def test_registers_mock_when_allowed(self):
        from unittest.mock import MagicMock

        from text_to_speech.api import _register_configured_providers

        _registry._providers.clear()
        mock_settings = MagicMock()
        mock_settings.TTS_PROVIDER = "mock"
        mock_settings.TTS_ALLOW_MOCK = True

        with patch("text_to_speech.api._settings", mock_settings):
            _register_configured_providers()

        assert "mock" in _registry.list_providers()
        assert "edge" not in _registry.list_providers()
        _registry._providers.clear()

    def test_raises_when_mock_not_allowed(self):
        from unittest.mock import MagicMock

        from text_to_speech.api import _register_configured_providers

        _registry._providers.clear()
        mock_settings = MagicMock()
        mock_settings.TTS_PROVIDER = "mock"
        mock_settings.TTS_ALLOW_MOCK = False

        with patch("text_to_speech.api._settings", mock_settings):
            with pytest.raises(RuntimeError, match="not allowed in production"):
                _register_configured_providers()

        assert len(_registry._providers) == 0

    def test_raises_for_unknown_provider(self):
        from unittest.mock import MagicMock

        from text_to_speech.api import _register_configured_providers

        _registry._providers.clear()
        mock_settings = MagicMock()
        mock_settings.TTS_PROVIDER = "unknown"
        mock_settings.TTS_ALLOW_MOCK = False

        with patch("text_to_speech.api._settings", mock_settings):
            with pytest.raises(ValueError, match="Unknown TTS provider"):
                _register_configured_providers()

        assert len(_registry._providers) == 0


class TestEngine:
    def test_generate_response_current_weather(self):
        engine = TextToSpeechEngine()
        insight = {
            "type": InsightType.CURRENT_WEATHER,
            "location": "Punjab",
            "value": 32,
            "values": {"rain_probability": 20, "rainfall": 10},
        }
        response = engine.generate_response(insight, language="en")
        assert response.text
        assert "Punjab" in response.text
        assert "32" in response.text
        assert "20" in response.text

    def test_generate_response_temperature(self):
        engine = TextToSpeechEngine()
        insight = {
            "type": InsightType.TEMPERATURE,
            "location": "Tamil Nadu",
            "value": 38,
            "temperature_feeling": "hot",
        }
        response = engine.generate_response(insight, language="en")
        assert response.text
        assert "Tamil Nadu" in response.text
        assert "hot" in response.text

    def test_generate_response_comparison(self):
        engine = TextToSpeechEngine()
        insight = {
            "type": InsightType.COMPARISON,
            "location_a": "Punjab",
            "location_b": "Maharashtra",
            "metric": "rainfall_mm",
            "value_a": 50,
            "value_b": 80,
            "difference": 30,
        }
        response = engine.generate_response(insight, language="en")
        assert response.text
        assert "Punjab" in response.text
        assert "Maharashtra" in response.text
        assert "50" in response.text
        assert "80" in response.text
        assert "30" in response.text

    def test_generate_response_trend(self):
        engine = TextToSpeechEngine()
        insight = {
            "type": InsightType.TREND,
            "metric": "rainfall_mm",
            "direction": "up",
            "magnitude": 15,
            "period": "week",
        }
        response = engine.generate_response(insight, language="en")
        assert response.text
        assert "increasing" in response.text
        assert "15" in response.text

    def test_generate_response_multilingual(self):
        engine = TextToSpeechEngine()
        insight = {
            "type": InsightType.CURRENT_WEATHER,
            "location": "Punjab",
            "value": 30,
            "values": {"rain_probability": 10, "rainfall": 5},
        }
        for lang in ["hi", "ta", "te", "kn", "mr", "bn"]:
            response = engine.generate_response(insight, language=lang)
            assert response.text
            assert response.language == lang

    def test_generate_response_preserves_numerical_accuracy(self):
        engine = TextToSpeechEngine()
        insight = {
            "type": InsightType.TEMPERATURE,
            "location": "Test",
            "value": 37.5,
        }
        response = engine.generate_response(insight, language="en")
        assert "37.5" in response.text


class TestDataset:
    def test_dataset_has_all_languages(self):
        for code in ["en", "hi"]:
            assert code in TEST_DATASET, f"Missing test phrases for {code}"

    def test_dataset_phrases_non_empty(self):
        for code, data in TEST_DATASET.items():
            for phrase in data.get("phrases", []):
                assert phrase.strip()
                assert len(phrase.split()) >= 1

    def test_dataset_weather_terms_covered(self):
        en_phrases = TEST_DATASET.get("en", {}).get("phrases", [])
        weather_terms = ["rain", "temperature", "yield", "soil moisture"]
        for term in weather_terms:
            assert any(term in p.lower() for p in en_phrases), f"Missing weather term: {term}"

    def test_dataset_numbers_covered(self):
        en_phrases = TEST_DATASET.get("en", {}).get("phrases", [])
        assert any(any(c.isdigit() for c in p) for p in en_phrases), "Dataset missing numeric phrases"


class TestAPIIntegration:
    def test_tts_routes_registered(self):
        from text_to_speech.api import router
        paths = [r.path for r in router.routes]
        assert "/languages" in paths
        assert "/localize" in paths
        assert "/synthesize" in paths
        assert "/synthesize-text" in paths
