from __future__ import annotations

from speech_to_text.languages import (
    LANGUAGE_CODE_MAP,
    SUPPORTED_LANGUAGES,
    UNSUPPORTED_LANGUAGE_ERROR,
    get_language_config,
    is_language_supported,
)
from speech_to_text.provider import (
    MockSpeechProvider,
    SpeechProvider,
    SpeechProviderRegistry,
    WhisperSpeechProvider,
    get_speech_provider,
    register_speech_provider,
)
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

__all__ = [
    "SpeechProvider",
    "MockSpeechProvider",
    "WhisperSpeechProvider",
    "SpeechProviderRegistry",
    "get_speech_provider",
    "register_speech_provider",
    "TranscriptionRequest",
    "TranscriptionResponse",
    "SpeechRecognitionResult",
    "SpeechRecognitionError",
    "SpeechRecognitionErrorCode",
    "RecognitionSegment",
    "AudioFormat",
    "NoiseLevel",
    "SUPPORTED_LANGUAGES",
    "LANGUAGE_CONFIG",
    "LANGUAGE_CODE_MAP",
    "get_language_config",
    "is_language_supported",
    "UNSUPPORTED_LANGUAGE_ERROR",
]
