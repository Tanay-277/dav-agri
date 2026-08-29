from __future__ import annotations

from text_to_speech.languages import (
    LANGUAGE_CODE_MAP,
    SUPPORTED_LANGUAGES,
    UNSUPPORTED_LANGUAGE_ERROR,
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
    TTSProvider,
    TTSProviderRegistry,
    get_tts_provider,
    register_tts_provider,
)
from text_to_speech.schemas import (
    AudioFormat,
    InsightType,
    LocalizedResponse,
    NumberFormat,
    SynthesisRequest,
    SynthesisResponse,
    TTSProviderError,
    TTSProviderErrorCode,
    VoiceGender,
)

__all__ = [
    "TTSProvider",
    "MockTTSProvider",
    "EdgeTTSProvider",
    "TTSProviderRegistry",
    "get_tts_provider",
    "register_tts_provider",
    "SynthesisRequest",
    "SynthesisResponse",
    "LocalizedResponse",
    "InsightType",
    "AudioFormat",
    "NumberFormat",
    "VoiceGender",
    "TTSProviderError",
    "TTSProviderErrorCode",
    "SUPPORTED_LANGUAGES",
    "LANGUAGE_CONFIG",
    "LANGUAGE_CODE_MAP",
    "get_language_config",
    "is_language_supported",
    "UNSUPPORTED_LANGUAGE_ERROR",
    "normalize_for_tts",
    "normalize_number",
    "normalize_unit",
]
