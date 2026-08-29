from __future__ import annotations

import json
import random
from unittest.mock import patch

import pytest

from speech_to_text.languages import (
    LANGUAGE_CODE_MAP,
    SUPPORTED_LANGUAGES,
    get_language_config,
    is_language_supported,
)
from speech_to_text.metrics import compute_batch_wer, wer, wer_details
from speech_to_text.normalizer import normalize_transcript
from speech_to_text.provider import (
    MockSpeechProvider,
    WhisperSpeechProvider,
    get_speech_provider,
    register_speech_provider,
)
from speech_to_text.schemas import (
    AudioFormat,
    NoiseLevel,
    RecognitionSegment,
    SpeechRecognitionErrorCode,
    SpeechRecognitionResult,
    TranscriptionRequest,
    TranscriptionResponse,
)

DATASET_PATH = None
try:
    import importlib.resources as pkg_resources
    from speech_to_text import dataset as dataset_mod
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
        "en": {"queries": ["what is the weather in punjab", "will it rain tomorrow", "how hot is it today"]},
        "hi": {"queries": ["mausam ka haal kya hai", "kya kal barish hogi"]},
    }


@pytest.fixture(autouse=True)
def _register_mock():
    register_speech_provider(MockSpeechProvider(dataset=TEST_DATASET))
    yield
    register_speech_provider(MockSpeechProvider())


class TestNormalizer:
    def test_removes_fillers(self):
        result = normalize_transcript("please show wheat in punjab")
        assert result == "show wheat in punjab"

    def test_lowercases(self):
        result = normalize_transcript("Will it rain TOMORROW")
        assert result == result.lower()

    def test_removes_punctuation(self):
        result = normalize_transcript("Will it rain tomorrow?")
        assert "?" not in result

    def test_collapses_whitespace(self):
        result = normalize_transcript("  hello    world  ")
        assert result == "hello world"

    def test_empty_transcript(self):
        assert normalize_transcript("") == ""
        assert normalize_transcript("   ") == ""


class TestLanguageConfig:
    def test_all_supported_languages_present(self):
        expected = {"en", "hi", "ta", "te", "kn", "mr", "bn"}
        assert set(SUPPORTED_LANGUAGES.keys()) == expected

    def test_is_language_supported(self):
        assert is_language_supported("en")
        assert is_language_supported("hi")
        assert is_language_supported("ta")
        assert not is_language_supported("fr")

    def test_language_code_map(self):
        assert LANGUAGE_CODE_MAP.get("english") == "en"
        assert LANGUAGE_CODE_MAP.get("hindi") == "hi"
        assert get_language_config("hi-IN") is not None
        assert get_language_config("hi-IN").code == "hi"

    def test_get_language_config(self):
        config = get_language_config("en")
        assert config.name == "English"
        assert config.bcp47_tag == "en-IN"


class TestMockProvider:
    @pytest.mark.asyncio
    async def test_empty_audio_returns_error(self):
        provider = get_speech_provider("mock")
        response = await provider.transcribe(b"", TranscriptionRequest(language="en"))
        assert response.success is False
        assert response.result is None

    @pytest.mark.asyncio
    async def test_successful_transcription(self):
        provider = get_speech_provider("mock")
        audio = b"some-audio-bytes-for-testing"
        response = await provider.transcribe(
            audio, TranscriptionRequest(language="en", noise_level=NoiseLevel.CLEAN)
        )
        assert response.success is True
        assert response.result is not None
        assert response.result.transcript
        assert response.result.normalized_transcript
        assert 0.0 <= response.result.confidence <= 1.0
        assert response.result.language == "en"
        assert response.result.provider == "mock"

    @pytest.mark.asyncio
    async def test_noise_level_affects_confidence(self):
        provider = get_speech_provider("mock")
        audio = b"audio-bytes-for-noise-test"
        clean = await provider.transcribe(
            audio, TranscriptionRequest(language="en", noise_level=NoiseLevel.CLEAN)
        )
        noisy = await provider.transcribe(
            audio, TranscriptionRequest(language="en", noise_level=NoiseLevel.HIGH)
        )
        assert clean.result.confidence >= noisy.result.confidence

    @pytest.mark.asyncio
    async def test_unsupported_language_fallback(self):
        provider = get_speech_provider("mock")
        response = await provider.transcribe(
            b"audio", TranscriptionRequest(language="fr")
        )
        assert response.success is True
        assert response.result.language == "en"

    @pytest.mark.asyncio
    async def test_processing_time_recorded(self):
        provider = get_speech_provider("mock")
        response = await provider.transcribe(
            b"audio", TranscriptionRequest(language="en")
        )
        assert response.result.processing_time_ms >= 50

    @pytest.mark.asyncio
    async def test_segments_returned_when_enabled(self):
        provider = get_speech_provider("mock")
        response = await provider.transcribe(
            b"audio",
            TranscriptionRequest(language="en", enable_segmentation=True),
        )
        assert isinstance(response.result.segments, list)

    @pytest.mark.asyncio
    async def test_multilingual_support(self):
        provider = get_speech_provider("mock")
        for code in ["hi", "ta", "te", "kn", "mr", "bn"]:
            response = await provider.transcribe(
                b"audio-bytes", TranscriptionRequest(language=code)
            )
            assert response.success is True, f"Failed for language {code}"
            assert response.result.language == code

    @pytest.mark.asyncio
    async def test_normalized_transcript_clean(self):
        provider = get_speech_provider("mock")
        response = await provider.transcribe(
            b"audio", TranscriptionRequest(language="en")
        )
        norm = response.result.normalized_transcript
        assert "  " not in norm
        assert norm == norm.strip()


class TestWhisperProvider:
    def test_import_fails_gracefully(self):
        provider = WhisperSpeechProvider()
        assert provider.name == "whisper"

    def test_supports_language_returns_false_without_model(self):
        provider = WhisperSpeechProvider()
        assert provider.supports_language("en") is False

    @pytest.mark.asyncio
    async def test_transcribe_returns_error_without_model(self):
        provider = WhisperSpeechProvider()
        with patch.object(provider, "_load_model", return_value=None):
            response = await provider.transcribe(b"audio", TranscriptionRequest(language="en"))
        assert response.success is False
        assert "not available" in response.message.lower()


class TestMetrics:
    def test_perfect_match(self):
        assert wer("hello world", "hello world") == 0.0

    def test_all_wrong(self):
        assert wer("hello world", "goodbye universe") == 1.0

    def test_empty_reference(self):
        assert wer("", "hello") == 1.0
        assert wer("", "") == 0.0

    def test_wer_details(self):
        details = wer_details("hello world", "hello there")
        assert "substitutions" in details
        assert "deletions" in details
        assert "insertions" in details
        assert "wer" in details
        assert 0.0 <= details["wer"] <= 1.0
        assert details["substitutions"] == 1
        assert details["deletions"] == 0
        assert details["insertions"] == 0

    def test_batch_wer(self):
        results = [
            {"reference": "hello world", "hypothesis": "hello world"},
            {"reference": "rain tomorrow", "hypothesis": "rain tomorrow"},
            {"reference": "temperature rising", "hypothesis": "temperature rising"},
        ]
        stats = compute_batch_wer(results)
        assert stats["wer"] == 0.0
        assert stats["count"] == 3

    def test_batch_wer_empty(self):
        assert compute_batch_wer([]) == {"wer": 0.0, "count": 0}

    def test_realistic_wer(self):
        ref = "will it rain tomorrow in punjab"
        hyp = "will it rain tomorrow in punjub"
        w = wer(ref, hyp)
        assert 0.0 < w < 0.5


class TestDataset:
    def test_dataset_has_all_languages(self):
        for code in SUPPORTED_LANGUAGES:
            assert code in TEST_DATASET, f"Missing test queries for {code}"
            assert len(TEST_DATASET[code]["queries"]) >= 3

    def test_dataset_queries_non_empty(self):
        for code, data in TEST_DATASET.items():
            for query in data["queries"]:
                assert query.strip()
                assert len(query.split()) >= 1

    def test_dataset_no_duplicates(self):
        for code, data in TEST_DATASET.items():
            queries = data["queries"]
            assert len(queries) == len(set(queries)), f"Duplicate queries found for {code}"

    def test_english_dataset_coverage(self):
        en_queries = TEST_DATASET.get("en", {}).get("queries", [])
        categories = {
            "weather": any("weather" in q.lower() for q in en_queries),
            "rain": any("rain" in q.lower() for q in en_queries),
            "temperature": any("temperature" in q.lower() for q in en_queries),
            "forecast": any("tomorrow" in q.lower() for q in en_queries),
            "comparison": any("compare" in q.lower() for q in en_queries),
            "follow_up": any("and" in q.lower() or "also" in q.lower() for q in en_queries),
        }
        for category, present in categories.items():
            assert present, f"English dataset missing {category} coverage"


class TestAPIIntegration:
    def test_list_languages_endpoint(self):
        from speech_to_text.api import router
        assert any(route.path == "/languages" for route in router.routes)

    def test_transcribe_endpoint_exists(self):
        from speech_to_text.api import router
        assert any(route.path == "/transcribe" and "POST" in route.methods for route in router.routes)
