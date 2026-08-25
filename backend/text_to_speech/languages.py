from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class LanguageConfig:
    code: str
    name: str
    bcp47_tag: str
    tts_voice_female: Optional[str] = None
    tts_voice_male: Optional[str] = None
    rtl: bool = False
    number_format: str = "cardinal"


SUPPORTED_LANGUAGES: dict[str, LanguageConfig] = {
    "en": LanguageConfig(
        code="en",
        name="English",
        bcp47_tag="en-IN",
        tts_voice_female="en-IN-NeerjaNeural",
        tts_voice_male="en-IN-PrabhatNeural",
    ),
    "hi": LanguageConfig(
        code="hi",
        name="Hindi",
        bcp47_tag="hi-IN",
        tts_voice_female="hi-IN-SwaraNeural",
        tts_voice_male="hi-IN-MadhurNeural",
    ),
    "ta": LanguageConfig(
        code="ta",
        name="Tamil",
        bcp47_tag="ta-IN",
        tts_voice_female="ta-IN-PallaviNeural",
        tts_voice_male="ta-IN-ValluvarNeural",
    ),
    "te": LanguageConfig(
        code="te",
        name="Telugu",
        bcp47_tag="te-IN",
        tts_voice_female="te-IN-MohanNeural",
        tts_voice_male="te-IN-MohanNeural",
    ),
    "kn": LanguageConfig(
        code="kn",
        name="Kannada",
        bcp47_tag="kn-IN",
        tts_voice_female="kn-IN-SapnaNeural",
        tts_voice_male="kn-IN-GaganNeural",
    ),
    "mr": LanguageConfig(
        code="mr",
        name="Marathi",
        bcp47_tag="mr-IN",
        tts_voice_female="mr-IN-AarohiNeural",
        tts_voice_male="mr-IN-ManoharNeural",
    ),
    "bn": LanguageConfig(
        code="bn",
        name="Bengali",
        bcp47_tag="bn-IN",
        tts_voice_female="bn-IN-TanishaaNeural",
        tts_voice_male="bn-IN-PrabirNeural",
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
    "Selected language is not supported by the text-to-speech system. "
    "Supported languages: English, Hindi, Tamil, Telugu, Kannada, Marathi, Bengali."
)


def get_language_config(language: str) -> Optional[LanguageConfig]:
    normalized = language.lower().strip()
    code = LANGUAGE_CODE_MAP.get(normalized, normalized)
    return SUPPORTED_LANGUAGES.get(code)


def is_language_supported(language: str) -> bool:
    return get_language_config(language) is not None
