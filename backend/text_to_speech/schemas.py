from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class InsightType(str, Enum):
    CURRENT_WEATHER = "current_weather"
    FORECAST = "forecast"
    RAIN_PROBABILITY = "rain_probability"
    TEMPERATURE = "temperature"
    COMPARISON = "comparison"
    TREND = "trend"
    WARNING = "warning"
    CLARIFICATION = "clarification"
    UNSUPPORTED = "unsupported"
    RECOMMENDATION = "recommendation"
    YIELD_REPORT = "yield_report"
    SOIL_MOISTURE = "soil_moisture"


class AudioFormat(str, Enum):
    MP3 = "mp3"
    WAV = "wav"
    OGG = "ogg"
    WEBM = "webm"


class VoiceGender(str, Enum):
    FEMALE = "female"
    MALE = "male"
    NEUTRAL = "neutral"


class NumberFormat(str, Enum):
    CARDINAL = "cardinal"
    ORDINAL = "ordinal"
    DIGIT = "digit"


class TTSProviderErrorCode(str, Enum):
    EMPTY_TEXT = "empty_text"
    LANGUAGE_NOT_SUPPORTED = "language_not_supported"
    PROVIDER_ERROR = "provider_error"
    NETWORK_ERROR = "network_error"
    AUDIO_TOO_LONG = "audio_too_long"
    PROCESSING_ERROR = "processing_error"


class TTSProviderError(BaseModel):
    code: TTSProviderErrorCode
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class LocalizedResponse(BaseModel):
    text: str = Field(..., description="Final localized text ready for TTS")
    language: str = Field(..., description="Language code")
    insight_type: InsightType = Field(..., description="Type of insight")
    original_values: dict[str, Any] = Field(
        default_factory=dict,
        description="Original numerical values from structured insight",
    )
    metadata: dict[str, Any] = Field(default_factory=dict)


class SynthesisRequest(BaseModel):
    text: str = Field(..., description="Text to synthesize")
    language: str = Field(default="en", description="BCP-47 language code")
    voice_gender: VoiceGender = Field(default=VoiceGender.FEMALE)
    voice_name: str | None = Field(default=None, description="Provider-specific voice name")
    rate: float = Field(default=1.0, ge=0.5, le=2.0, description="Speech rate multiplier")
    pitch: float = Field(default=1.0, ge=0.5, le=2.0, description="Pitch multiplier")
    output_format: AudioFormat = Field(default=AudioFormat.MP3)
    max_duration_ms: int = Field(default=30000, ge=1000, le=300000)


class SynthesisResponse(BaseModel):
    audio_url: str | None = Field(default=None, description="URL or path to generated audio")
    audio_bytes: bytes | None = Field(default=None, description="Raw audio bytes")
    content_type: str = Field(default="audio/mpeg", description="MIME type of audio")
    duration_ms: int = Field(default=0, ge=0, description="Duration of generated audio")
    provider: str = Field(..., description="TTS provider used")
    success: bool = Field(..., description="Whether synthesis succeeded")
    message: str = Field(default="", description="Human-readable status message")
    error: TTSProviderError | None = Field(default=None)
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional provider-specific metadata")
