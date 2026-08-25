from __future__ import annotations

import os
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AudioFormat(str, Enum):
    WAV = "wav"
    MP3 = "mp3"
    OGG = "ogg"
    WEBM = "webm"
    M4A = "m4a"
    FLAC = "flac"


class NoiseLevel(str, Enum):
    CLEAN = "clean"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SpeechRecognitionErrorCode(str, Enum):
    EMPTY_AUDIO = "empty_audio"
    UNSUPPORTED_FORMAT = "unsupported_format"
    NO_SPEECH = "no_speech"
    NOISE_ERROR = "noise_error"
    LANGUAGE_NOT_SUPPORTED = "language_not_supported"
    PROVIDER_ERROR = "provider_error"
    AUDIO_TOO_LONG = "audio_too_long"
    PERMISSION_DENIED = "permission_denied"
    NETWORK_ERROR = "network_error"
    PROCESSING_ERROR = "processing_error"


class SpeechRecognitionError(BaseModel):
    code: SpeechRecognitionErrorCode
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class RecognitionSegment(BaseModel):
    start_ms: int = Field(..., ge=0, description="Start time in milliseconds")
    end_ms: int = Field(..., ge=0, description="End time in milliseconds")
    text: str = Field(..., description="Transcribed text for this segment")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")


class SpeechRecognitionResult(BaseModel):
    transcript: str = Field(..., description="Full transcript from STT")
    normalized_transcript: str = Field(..., description="Normalized transcript for NLU")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence score")
    language: str = Field(..., description="Detected or selected language code")
    detected_language: str | None = Field(default=None, description="Auto-detected language if different")
    provider: str = Field(..., description="Name of the STT provider used")
    processing_time_ms: int = Field(..., ge=0, description="Processing time in milliseconds")
    segments: list[RecognitionSegment] = Field(default_factory=list, description="Per-segment results")
    error: SpeechRecognitionError | None = Field(default=None, description="Error details if any")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional provider-specific metadata")


class TranscriptionRequest(BaseModel):
    language: str = Field(default="en", description="BCP-47 language code (e.g., 'en', 'hi-IN')")
    auto_detect_language: bool = Field(default=False, description="Whether to auto-detect language")
    expected_duration_ms: int | None = Field(default=None, ge=0, description="Expected audio duration hint")
    noise_level: NoiseLevel = Field(default=NoiseLevel.CLEAN, description="Estimated background noise level")
    enable_segmentation: bool = Field(default=True, description="Return per-segment timestamps")
    max_audio_duration_ms: int = Field(default=30000, ge=1000, le=300000, description="Maximum allowed audio length")
    audio_format: AudioFormat | None = Field(default=None, description="Format hint for the uploaded audio")


class TranscriptionResponse(BaseModel):
    result: SpeechRecognitionResult | None = Field(default=None)
    success: bool = Field(..., description="Whether transcription succeeded")
    message: str = Field(default="", description="Human-readable status message")
