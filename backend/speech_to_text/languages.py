from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class LanguageConfig:
    code: str
    name: str
    bcp47_tag: str
    whisper_model: Optional[str] = None
    tts_voice_hint: Optional[str] = None
    rtl: bool = False


SUPPORTED_LANGUAGES: dict[str, LanguageConfig] = {
    "en": LanguageConfig(
        code="en",
        name="English",
        bcp47_tag="en-IN",
        whisper_model="Systran/faster-whisper-small",
        tts_voice_hint="en-IN",
    ),
    "hi": LanguageConfig(
        code="hi",
        name="Hindi",
        bcp47_tag="hi-IN",
        whisper_model="Systran/faster-whisper-small",
        tts_voice_hint="hi-IN",
    ),
    "ta": LanguageConfig(
        code="ta",
        name="Tamil",
        bcp47_tag="ta-IN",
        whisper_model="Systran/faster-whisper-small",
        tts_voice_hint="ta-IN",
    ),
    "te": LanguageConfig(
        code="te",
        name="Telugu",
        bcp47_tag="te-IN",
        whisper_model="Systran/faster-whisper-small",
        tts_voice_hint="te-IN",
    ),
    "kn": LanguageConfig(
        code="kn",
        name="Kannada",
        bcp47_tag="kn-IN",
        whisper_model="Systran/faster-whisper-small",
        tts_voice_hint="kn-IN",
    ),
    "mr": LanguageConfig(
        code="mr",
        name="Marathi",
        bcp47_tag="mr-IN",
        whisper_model="Systran/faster-whisper-small",
        tts_voice_hint="mr-IN",
    ),
    "bn": LanguageConfig(
        code="bn",
        name="Bengali",
        bcp47_tag="bn-IN",
        whisper_model="Systran/faster-whisper-small",
        tts_voice_hint="bn-IN",
    ),
}

LANGUAGE_CODE_MAP: dict[str, str] = {
    "english": "en",
    "hindi": "hi",
    "tamil": "ta",
    "telugu": "te",
    "kannada": "kn",
    "marathi": "mr",
    "bengali": "bn",
    "en": "en",
    "hi": "hi",
    "ta": "ta",
    "te": "te",
    "kn": "kn",
    "mr": "mr",
    "bn": "bn",
    "en-in": "en",
    "hi-in": "hi",
    "ta-in": "ta",
    "te-in": "te",
    "kn-in": "kn",
    "mr-in": "mr",
    "bn-in": "bn",
}

UNSUPPORTED_LANGUAGE_ERROR = (
    "Selected language is not supported by the current speech provider. "
    "Supported languages: English, Hindi, Tamil, Telugu, Kannada, Marathi, Bengali."
)


def get_language_config(language: str) -> LanguageConfig | None:
    normalized = language.lower().strip()
    code = LANGUAGE_CODE_MAP.get(normalized, normalized)
    return SUPPORTED_LANGUAGES.get(code)


def is_language_supported(language: str) -> bool:
    return get_language_config(language) is not None
