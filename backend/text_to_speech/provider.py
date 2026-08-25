from __future__ import annotations

import asyncio
import logging
import os
import tempfile
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from text_to_speech.languages import (
    LANGUAGE_CODE_MAP,
    SUPPORTED_LANGUAGES,
    UNSUPPORTED_LANGUAGE_ERROR,
    get_language_config,
    is_language_supported,
)
from text_to_speech.normalizer import normalize_for_tts, normalize_number
from text_to_speech.schemas import (
    AudioFormat,
    TTSProviderError,
    TTSProviderErrorCode,
    VoiceGender,
    SynthesisRequest,
    SynthesisResponse,
)

logger = logging.getLogger(__name__)

MAX_TEXT_LENGTH = 5000
OUTPUT_DIR = Path("/tmp/agristory-tts")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class TTSProvider(ABC):
    """Abstract base class for text-to-speech providers."""

    name: str = "base"

    @abstractmethod
    async def synthesize(
        self, request: SynthesisRequest
    ) -> SynthesisResponse:
        """Synthesize speech from text."""

    @abstractmethod
    def supports_language(self, language: str) -> bool:
        """Return True if the provider can handle the given language."""

    def _validate_request(self, request: SynthesisRequest) -> TTSProviderError | None:
        if not request.text or not request.text.strip():
            return TTSProviderError(
                code=TTSProviderErrorCode.EMPTY_TEXT,
                message="Text to synthesize is empty.",
            )
        if len(request.text) > MAX_TEXT_LENGTH:
            return TTSProviderError(
                code=TTSProviderErrorCode.AUDIO_TOO_LONG,
                message=f"Text exceeds maximum length of {MAX_TEXT_LENGTH} characters.",
                details={"max_length": MAX_TEXT_LENGTH, "received_length": len(request.text)},
            )
        return None

    def _resolve_language(self, request: SynthesisRequest) -> tuple[str, str | None]:
        normalized = request.language.lower().strip()
        code = LANGUAGE_CODE_MAP.get(normalized, normalized)
        if is_language_supported(code):
            return code, None
        return "en", code

    def _resolve_voice(self, request: SynthesisRequest, language_code: str) -> str | None:
        config = get_language_config(language_code)
        if not config:
            return None
        if request.voice_name:
            return request.voice_name
        if request.voice_gender == VoiceGender.MALE and config.tts_voice_male:
            return config.tts_voice_male
        if config.tts_voice_female:
            return config.tts_voice_female
        return None


class TTSProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, TTSProvider] = {}

    def register(self, provider: TTSProvider) -> None:
        self._providers[provider.name] = provider
        logger.info("Registered TTS provider: %s", provider.name)

    def get(self, name: str) -> TTSProvider | None:
        return self._providers.get(name)

    def get_default(self) -> TTSProvider:
        if not self._providers:
            raise RuntimeError("No TTS providers registered.")
        return next(iter(self._providers.values()))

    def list_providers(self) -> list[str]:
        return list(self._providers.keys())


_registry = TTSProviderRegistry()


def register_tts_provider(provider: TTSProvider) -> None:
    _registry.register(provider)


def get_tts_provider(name: str | None = None) -> TTSProvider:
    if name:
        provider = _registry.get(name)
        if not provider:
            raise ValueError(f"TTS provider '{name}' is not registered.")
        return provider
    return _registry.get_default()


class MockTTSProvider(TTSProvider):
    name = "mock"

    def supports_language(self, language: str) -> bool:
        return is_language_supported(language)

    async def synthesize(
        self, request: SynthesisRequest
    ) -> SynthesisResponse:
        start = time.perf_counter()
        validation_error = self._validate_request(request)
        if validation_error:
            return SynthesisResponse(
                success=False,
                provider=self.name,
                error=validation_error,
                message=validation_error.message,
            )

        language_code, detected = self._resolve_language(request)
        lang_config = get_language_config(language_code)
        if not lang_config:
            return SynthesisResponse(
                success=False,
                provider=self.name,
                error=TTSProviderError(
                    code=TTSProviderErrorCode.LANGUAGE_NOT_SUPPORTED,
                    message=UNSUPPORTED_LANGUAGE_ERROR,
                ),
                message=UNSUPPORTED_LANGUAGE_ERROR,
            )

        voice = self._resolve_voice(request, language_code)
        normalized_text = normalize_for_tts(request.text, language=language_code)
        duration_ms = max(500, int(len(normalized_text) * 50 / request.rate))

        audio_bytes = self._generate_silent_audio(duration_ms)
        processing_time_ms = int((time.perf_counter() - start) * 1000)
        if processing_time_ms < 50:
            processing_time_ms = 50

        return SynthesisResponse(
            success=True,
            provider=self.name,
            audio_bytes=audio_bytes,
            content_type="audio/mpeg",
            duration_ms=duration_ms,
            message="Synthesis completed (mock).",
            metadata={
                "language": language_code,
                "detected_language": detected,
                "voice": voice,
                "normalized_text": normalized_text,
                "simulated": True,
            },
        )

    def _generate_silent_audio(self, duration_ms: int) -> bytes:
        """Generate a minimal silent MP3-like payload for testing."""
        return f"MOCK_AUDIO_{duration_ms}ms".encode("utf-8")


class EdgeTTSProvider(TTSProvider):
    name = "edge"

    def __init__(self, output_dir: Path | None = None) -> None:
        self.output_dir = output_dir or OUTPUT_DIR
        self._available = False
        self._load_client()

    def _load_client(self) -> None:
        try:
            import edge_tts  # type: ignore[import-untyped]
            self._edge_tts = edge_tts
            self._available = True
            logger.info("EdgeTTS provider loaded.")
        except ImportError:
            logger.warning("edge-tts is not installed. Install it with: pip install edge-tts")
            self._available = False

    def supports_language(self, language: str) -> bool:
        if not self._available:
            return False
        return is_language_supported(language)

    async def synthesize(
        self, request: SynthesisRequest
    ) -> SynthesisResponse:
        start = time.perf_counter()
        validation_error = self._validate_request(request)
        if validation_error:
            return SynthesisResponse(
                success=False,
                provider=self.name,
                error=validation_error,
                message=validation_error.message,
            )

        if not self._available:
            return SynthesisResponse(
                success=False,
                provider=self.name,
                error=TTSProviderError(
                    code=TTSProviderErrorCode.PROVIDER_ERROR,
                    message="edge-tts is not installed.",
                ),
                message="edge-tts is not installed. Install it with: pip install edge-tts",
            )

        language_code, detected = self._resolve_language(request)
        lang_config = get_language_config(language_code)
        if not lang_config:
            return SynthesisResponse(
                success=False,
                provider=self.name,
                error=TTSProviderError(
                    code=TTSProviderErrorCode.LANGUAGE_NOT_SUPPORTED,
                    message=UNSUPPORTED_LANGUAGE_ERROR,
                ),
                message=UNSUPPORTED_LANGUAGE_ERROR,
            )

        voice = self._resolve_voice(request, language_code)
        normalized_text = normalize_for_tts(request.text, language=language_code)
        safe_name = "".join(c if c.isalnum() else "_" for c in normalized_text[:30])
        output_path = self.output_dir / f"{int(time.time()*1000)}_{safe_name}.mp3"

        try:
            communicate = self._edge_tts.Communicate(
                text=normalized_text,
                voice=voice or f"{language_code}-{lang_config.bcp47_tag.split('-')[-1]}-Neural",
                rate=f"{int((request.rate - 1) * 100):+d}%",
                pitch=f"{int((request.pitch - 1) * 100):+d}%",
            )
            await communicate.save(str(output_path))

            audio_bytes = output_path.read_bytes()
            duration_ms = max(500, int(len(normalized_text) * 50 / request.rate))
            processing_time_ms = int((time.perf_counter() - start) * 1000)

            return SynthesisResponse(
                success=True,
                provider=self.name,
                audio_url=f"/tmp/agristory-tts/{output_path.name}",
                audio_bytes=audio_bytes,
                content_type="audio/mpeg",
                duration_ms=duration_ms,
                message="Synthesis completed.",
                metadata={
                    "language": language_code,
                    "detected_language": detected,
                    "voice": voice,
                    "normalized_text": normalized_text,
                    "file_path": str(output_path),
                },
            )
        except Exception as exc:
            logger.exception("EdgeTTS synthesis failed: %s", exc)
            return SynthesisResponse(
                success=False,
                provider=self.name,
                error=TTSProviderError(
                    code=TTSProviderErrorCode.PROCESSING_ERROR,
                    message=str(exc),
                ),
                message=f"Synthesis failed: {exc}",
            )
