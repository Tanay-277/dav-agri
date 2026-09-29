import base64
import logging
from typing import Tuple
from app.voice import get_stt_provider, get_tts_provider
from app.schemas.voice import TranscribeResponse, VoiceSampleResponse

logger = logging.getLogger(__name__)

# Exact preview sentences matching specification
SAMPLE_PHRASES = {
    "en": "Hello, I am your voice assistant.",
    "hi": "नमस्ते, मैं आपका वॉइस असिस्टेंट हूँ।",
    "mr": "नमस्कार, मी तुमचा व्हॉइस असिस्टंट आहे।"
}

class VoiceService:
    def __init__(self):
        self.stt_provider = get_stt_provider()
        self.tts_provider = get_tts_provider()

    def transcribe_audio(self, audio_bytes: bytes, language: str = "mr") -> TranscribeResponse:
        text, confidence = self.stt_provider.transcribe(audio_bytes, language)
        return TranscribeResponse(
            text=text,
            confidence=confidence,
            language=language
        )

    def synthesize_speech(self, text: str, language: str = "mr") -> bytes:
        return self.tts_provider.synthesize(text, language)

    def get_sample_for_language(self, language: str = "mr") -> VoiceSampleResponse:
        clean_lang = language.lower().strip()
        if clean_lang not in SAMPLE_PHRASES:
            raise ValueError(f"Invalid language '{language}'. Must be one of {list(SAMPLE_PHRASES.keys())}")
        sample_text = SAMPLE_PHRASES[clean_lang]
        logger.info(f"Synthesizing preview speech for language '{clean_lang}': '{sample_text}'")
        audio_bytes = self.synthesize_speech(sample_text, clean_lang)
        b64_audio = base64.b64encode(audio_bytes).decode("ascii")
        return VoiceSampleResponse(
            language=language,
            sample_text=sample_text,
            audio_base64=b64_audio,
            mime_type="audio/mpeg"
        )
