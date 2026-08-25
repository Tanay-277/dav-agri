from __future__ import annotations

import logging
from typing import Any

from speech_to_text.languages import get_language_config, is_language_supported
from speech_to_text.provider import get_speech_provider
from speech_to_text.schemas import (
    NoiseLevel,
    TranscriptionRequest,
    TranscriptionResponse,
)

logger = logging.getLogger(__name__)


class SpeechToTextEngine:
    """High-level engine that combines speech recognition with NLU integration.

    This class orchestrates:
    1. Audio validation and language resolution
    2. Transcription via a pluggable provider
    3. Confidence-based fallback handling
    4. Normalization and NLU handoff
    """

    def __init__(self, provider_name: str | None = None) -> None:
        self.provider_name = provider_name
        try:
            self._provider = get_speech_provider(provider_name)
        except RuntimeError:
            from speech_to_text.provider import MockSpeechProvider, register_speech_provider
            register_speech_provider(MockSpeechProvider())
            self._provider = get_speech_provider(provider_name)

    async def process_audio(
        self,
        audio_bytes: bytes,
        language: str = "en",
        auto_detect: bool = False,
        noise_level: str = "clean",
        nlu_engine: Any = None,
    ) -> dict[str, Any]:
        """Transcribe audio and optionally pass to NLU engine.

        Returns a dict with keys:
        - success: bool
        - transcript: str | None
        - normalized_transcript: str | None
        - language: str
        - confidence: float
        - nlu_result: Any | None
        - error: str | None
        - provider: str
        - processing_time_ms: int
        """
        if not is_language_supported(language):
            return {
                "success": False,
                "transcript": None,
                "normalized_transcript": None,
                "language": language,
                "confidence": 0.0,
                "nlu_result": None,
                "error": f"Language '{language}' is not supported.",
                "provider": self._provider.name,
                "processing_time_ms": 0,
            }

        try:
            noise_enum = NoiseLevel(noise_level.lower())
        except ValueError:
            noise_enum = NoiseLevel.CLEAN

        request = TranscriptionRequest(
            language=language,
            auto_detect_language=auto_detect,
            noise_level=noise_enum,
            enable_segmentation=True,
        )

        response = await self._provider.transcribe(audio_bytes, request)

        if not response.success or not response.result:
            return {
                "success": False,
                "transcript": None,
                "normalized_transcript": None,
                "language": language,
                "confidence": 0.0,
                "nlu_result": None,
                "error": response.message or "Transcription failed.",
                "provider": self._provider.name,
                "processing_time_ms": response.result.processing_time_ms if response.result else 0,
            }

        result = response.result
        nlu_result = None
        if nlu_engine is not None:
            try:
                nlu_result = nlu_engine.parse(result.normalized_transcript, context={"language": result.language})
            except Exception as exc:
                logger.warning("NLU processing failed: %s", exc)
                nlu_result = None

        return {
            "success": True,
            "transcript": result.transcript,
            "normalized_transcript": result.normalized_transcript,
            "language": result.language,
            "confidence": result.confidence,
            "nlu_result": nlu_result,
            "error": None,
            "provider": result.provider,
            "processing_time_ms": result.processing_time_ms,
        }

    def process_text(self, text: str, language: str = "en", nlu_engine: Any = None) -> dict[str, Any]:
        """Process raw text input directly, bypassing STT.

        Useful for text input fallback or testing.
        """
        from speech_to_text.normalizer import normalize_transcript
        normalized = normalize_transcript(text, language=language)
        nlu_result = None
        if nlu_engine is not None:
            try:
                nlu_result = nlu_engine.parse(normalized, context={"language": language})
            except Exception as exc:
                logger.warning("NLU processing failed: %s", exc)
        return {
            "success": True,
            "transcript": text,
            "normalized_transcript": normalized,
            "language": language,
            "confidence": 1.0,
            "nlu_result": nlu_result,
            "error": None,
            "provider": "text_input",
            "processing_time_ms": 0,
        }
