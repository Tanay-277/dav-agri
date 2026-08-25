from __future__ import annotations

import asyncio
import hashlib
import logging
import os
import tempfile
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from speech_to_text.languages import (
    LANGUAGE_CODE_MAP,
    SUPPORTED_LANGUAGES,
    UNSUPPORTED_LANGUAGE_ERROR,
    get_language_config,
    is_language_supported,
)
from speech_to_text.normalizer import normalize_transcript
from speech_to_text.schemas import (
    AudioFormat,
    NoiseLevel,
    RecognitionSegment,
    SpeechRecognitionError,
    SpeechRecognitionErrorCode,
    SpeechRecognitionResult,
    TranscriptionRequest,
    TranscriptionResponse,
)

logger = logging.getLogger(__name__)

MAX_AUDIO_BYTES = 50 * 1024 * 1024
ALLOWED_EXTENSIONS = {".wav", ".mp3", ".ogg", ".webm", ".m4a", ".flac"}


class SpeechProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def transcribe(
        self, audio_bytes: bytes, request: TranscriptionRequest
    ) -> TranscriptionResponse:
        ...

    @abstractmethod
    def supports_language(self, language: str) -> bool:
        ...

    def _validate_audio(self, audio_bytes: bytes, request: TranscriptionRequest) -> SpeechRecognitionError | None:
        if len(audio_bytes) == 0:
            return SpeechRecognitionError(
                code=SpeechRecognitionErrorCode.EMPTY_AUDIO,
                message="Uploaded audio is empty.",
            )
        if len(audio_bytes) > MAX_AUDIO_BYTES:
            return SpeechRecognitionError(
                code=SpeechRecognitionErrorCode.AUDIO_TOO_LONG,
                message=f"Audio exceeds maximum size of {MAX_AUDIO_BYTES // (1024 * 1024)} MB.",
                details={"max_bytes": MAX_AUDIO_BYTES, "received_bytes": len(audio_bytes)},
            )
        return None

    def _resolve_language(self, request: TranscriptionRequest) -> tuple[str, str | None]:
        normalized = request.language.lower().strip()
        code = LANGUAGE_CODE_MAP.get(normalized, normalized)
        if request.auto_detect_language:
            return code, None
        detected = None
        if is_language_supported(code):
            return code, detected
        detected = code
        fallback = "en"
        return fallback, detected


class SpeechProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, SpeechProvider] = {}

    def register(self, provider: SpeechProvider) -> None:
        self._providers[provider.name] = provider
        logger.info("Registered speech provider: %s", provider.name)

    def get(self, name: str) -> SpeechProvider | None:
        return self._providers.get(name)

    def get_default(self) -> SpeechProvider:
        if not self._providers:
            raise RuntimeError("No speech providers registered.")
        return next(iter(self._providers.values()))

    def list_providers(self) -> list[str]:
        return list(self._providers.keys())


_registry = SpeechProviderRegistry()


def register_speech_provider(provider: SpeechProvider) -> None:
    _registry.register(provider)


def get_speech_provider(name: str | None = None) -> SpeechProvider:
    if name:
        provider = _registry.get(name)
        if not provider:
            raise ValueError(f"Speech provider '{name}' is not registered.")
        return provider
    return _registry.get_default()


class MockSpeechProvider(SpeechProvider):
    name = "mock"

    def __init__(self, dataset: dict[str, dict[str, list[str]]] | None = None) -> None:
        self.dataset = dataset or {}
        self._noise_models = {
            NoiseLevel.CLEAN: {"substitution_rate": 0.02, "deletion_rate": 0.01, "insertion_rate": 0.01},
            NoiseLevel.LOW: {"substitution_rate": 0.08, "deletion_rate": 0.03, "insertion_rate": 0.03},
            NoiseLevel.MEDIUM: {"substitution_rate": 0.18, "deletion_rate": 0.08, "insertion_rate": 0.06},
            NoiseLevel.HIGH: {"substitution_rate": 0.30, "deletion_rate": 0.15, "insertion_rate": 0.10},
        }

    def supports_language(self, language: str) -> bool:
        return is_language_supported(language)

    async def transcribe(
        self, audio_bytes: bytes, request: TranscriptionRequest
    ) -> TranscriptionResponse:
        start = time.perf_counter()
        validation_error = self._validate_audio(audio_bytes, request)
        if validation_error:
            return TranscriptionResponse(success=False, result=None, message=validation_error.message)

        language_code, detected = self._resolve_language(request)
        lang_config = get_language_config(language_code)
        if not lang_config:
            return TranscriptionResponse(
                success=False,
                result=None,
                message=UNSUPPORTED_LANGUAGE_ERROR,
            )

        try:
            reference_text = self._select_reference(audio_bytes, language_code, request)
        except Exception as exc:
            logger.error("Mock provider failed to select reference: %s", exc)
            return TranscriptionResponse(
                success=False,
                result=None,
                message="Failed to process audio with mock provider.",
            )

        noise = self._noise_models.get(request.noise_level, self._noise_models[NoiseLevel.CLEAN])
        hypothesis, segments = self._simulate_recognition(reference_text, noise)

        processing_time_ms = int((time.perf_counter() - start) * 1000)
        if processing_time_ms < 50:
            processing_time_ms = 50

        confidence = self._estimate_confidence(reference_text, hypothesis, noise)

        normalized = normalize_transcript(hypothesis, language=language_code)

        result = SpeechRecognitionResult(
            transcript=hypothesis,
            normalized_transcript=normalized,
            confidence=confidence,
            language=language_code,
            detected_language=detected,
            provider=self.name,
            processing_time_ms=processing_time_ms,
            segments=segments,
            metadata={
                "noise_level": request.noise_level.value,
                "simulated": True,
            },
        )
        return TranscriptionResponse(success=True, result=result, message="Transcription completed.")

    def _select_reference(self, audio_bytes: bytes, language_code: str, request: TranscriptionRequest) -> str:
        digest = hashlib.sha256(audio_bytes).hexdigest()
        index = int(digest[:8], 16)
        lang_queries = self.dataset.get(language_code, {}).get("queries", [])
        if not lang_queries:
            return f"reference query {index} in {language_code}"
        return lang_queries[index % len(lang_queries)]

    def _simulate_recognition(self, reference: str, noise: dict[str, float]) -> tuple[str, list[RecognitionSegment]]:
        words = reference.split()
        result: list[str] = []
        segments: list[RecognitionSegment] = []
        current_ms = 0
        for word in words:
            ms_per_word = max(300, min(800, len(word) * 60 + 200))
            import random
            rand = random.random()
            if rand < noise["deletion_rate"]:
                continue
            if rand < noise["deletion_rate"] + noise["substitution_rate"]:
                result.append(self._corrupt_word(word))
            else:
                result.append(word)
            segments.append(
                RecognitionSegment(
                    start_ms=current_ms,
                    end_ms=current_ms + ms_per_word,
                    text=result[-1] if result else word,
                    confidence=max(0.4, 1.0 - noise["substitution_rate"] - random.uniform(0, 0.1)),
                )
            )
            current_ms += ms_per_word
        if random.random() < noise["insertion_rate"]:
            filler = ["um", "uh", "hm", "mm", "aah"][random.randint(0, 4)]
            result.insert(random.randint(0, len(result)), filler)
        return " ".join(result) if result else reference, segments

    def _corrupt_word(self, word: str) -> str:
        import random
        if len(word) <= 2:
            return word
        ops = ["swap", "drop", "double", "mishear"]
        op = random.choice(ops)
        if op == "swap" and len(word) > 2:
            i = random.randint(0, len(word) - 2)
            chars = list(word)
            chars[i], chars[i + 1] = chars[i + 1], chars[i]
            return "".join(chars)
        if op == "drop":
            i = random.randint(0, len(word) - 1)
            return word[:i] + word[i + 1:]
        if op == "double":
            i = random.randint(0, len(word) - 1)
            return word[: i + 1] + word[i:]
        mishearings = {
            "rain": "rane", "temperature": "temperatur", "yield": "yeld",
            "moisture": "moister", "forecast": "forcast", "wheat": "wheat",
            "punjab": "punjub", "karnataka": "karnatak", "tamil": "tamill",
        }
        return mishearings.get(word.lower(), word)

    def _estimate_confidence(self, reference: str, hypothesis: str, noise: dict[str, float]) -> float:
        ref_words = reference.split()
        hyp_words = hypothesis.split()
        if not ref_words:
            return 0.5
        correct = sum(1 for w in ref_words if w in hyp_words)
        base = correct / len(ref_words)
        penalty = (noise["substitution_rate"] + noise["deletion_rate"]) * 0.5
        return max(0.3, min(0.98, base - penalty + 0.6))


class WhisperSpeechProvider(SpeechProvider):
    name = "whisper"

    def __init__(self, model_size: str = "small") -> None:
        self.model_size = model_size
        self._model = None
        self._load_model()

    def _load_model(self) -> None:
        try:
            from faster_whisper import WhisperModel
            self._model = WhisperModel(
                self.model_size,
                device="cpu",
                compute_type="int8",
            )
            logger.info("Loaded Whisper model: %s", self.model_size)
        except ImportError:
            logger.warning("faster-whisper is not installed. Whisper provider will fail at runtime.")
            self._model = None

    def supports_language(self, language: str) -> bool:
        if self._model is None:
            return False
        return is_language_supported(language)

    async def transcribe(
        self, audio_bytes: bytes, request: TranscriptionRequest
    ) -> TranscriptionResponse:
        start = time.perf_counter()
        validation_error = self._validate_audio(audio_bytes, request)
        if validation_error:
            return TranscriptionResponse(success=False, result=None, message=validation_error.message)

        if self._model is None:
            return TranscriptionResponse(
                success=False,
                result=None,
                message="Whisper model is not available. Install faster-whisper or use a different provider.",
            )

        language_code, detected = self._resolve_language(request)
        lang_config = get_language_config(language_code)
        if not lang_config:
            return TranscriptionResponse(
                success=False,
                result=None,
                message=UNSUPPORTED_LANGUAGE_ERROR,
            )

        tmp_path = None
        try:
            suffix = ".wav"
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name

            loop = asyncio.get_event_loop()
            segments_iter, info = await loop.run_in_executor(
                None,
                lambda: self._model.transcribe(
                    tmp_path,
                    language=language_code if not request.auto_detect_language else None,
                    beam_size=5,
                    vad_filter=True,
                    vad_parameters=dict(min_silence_duration_ms=500),
                ),
            )

            segments: list[RecognitionSegment] = []
            transcript_parts: list[str] = []
            for segment in segments_iter:
                text = segment.text.strip()
                transcript_parts.append(text)
                segments.append(
                    RecognitionSegment(
                        start_ms=int(segment.start * 1000),
                        end_ms=int(segment.end * 1000),
                        text=text,
                        confidence=float(segment.avg_logprob or -0.5),
                    )
                )

            raw_transcript = " ".join(transcript_parts).strip()
            if not raw_transcript:
                return TranscriptionResponse(
                    success=False,
                    result=None,
                    message="No speech detected in the audio.",
                )

            normalized = normalize_transcript(raw_transcript, language=language_code)
            confidence = self._compute_confidence(segments)
            processing_time_ms = int((time.perf_counter() - start) * 1000)

            result = SpeechRecognitionResult(
                transcript=raw_transcript,
                normalized_transcript=normalized,
                confidence=confidence,
                language=language_code,
                detected_language=detected or (info.language if hasattr(info, "language") else None),
                provider=self.name,
                processing_time_ms=processing_time_ms,
                segments=segments if request.enable_segmentation else [],
                metadata={
                    "model": self.model_size,
                    "duration": info.duration if hasattr(info, "duration") else None,
                },
            )
            return TranscriptionResponse(success=True, result=result, message="Transcription completed.")

        except Exception as exc:
            logger.exception("Whisper transcription failed: %s", exc)
            return TranscriptionResponse(
                success=False,
                result=None,
                message=f"Transcription failed: {exc}",
            )
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def _compute_confidence(self, segments: list[RecognitionSegment]) -> float:
        if not segments:
            return 0.5
        avg = sum(s.confidence for s in segments) / len(segments)
        return max(0.0, min(1.0, avg))
