import io
import logging
import asyncio
import concurrent.futures
from typing import Tuple, Dict
from app.voice.base import BaseSTTProvider, BaseTTSProvider
from app.voice.audio_utils import validate_audio_payload

logger = logging.getLogger(__name__)

class MockSTTProvider(BaseSTTProvider):
    def transcribe(self, audio_bytes: bytes, language: str = "mr") -> Tuple[str, float]:
        validate_audio_payload(audio_bytes)
        clean_lang = language.lower().strip()
        if clean_lang not in ("en", "hi", "mr"):
            raise ValueError(f"Unsupported language code '{language}'. Must be one of ['en', 'hi', 'mr']")

        if clean_lang == "mr":
            text = "माझ्या कापूस उत्पादनाची माहिती आणि खर्चाचा तक्ता दाखवा"
        elif clean_lang == "hi":
            text = "मेरी कपास उत्पादन और खर्च की जानकारी बताएं"
        else:
            text = "My cotton production was 12 quintals in 2022, 15 in 2023, 18 in 2024, and 21 in 2025. Show me how my production has changed over the years."

        return (text, 0.98)


class EdgeNeuralTTSProvider(BaseTTSProvider):
    """
    Microsoft Edge Neural Speech Synthesis provider.
    Delivers natural human voices in Marathi, Hindi, and English without requiring external API keys.
    """
    VOICE_MAP: Dict[str, str] = {
        "mr": "mr-IN-AarohiNeural",
        "hi": "hi-IN-MadhurNeural",
        "en": "en-IN-NeerjaNeural",
    }

    async def _synthesize_async(self, text: str, voice: str) -> bytes:
        import edge_tts
        communicate = edge_tts.Communicate(text, voice)
        audio_stream = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_stream += chunk["data"]
        return audio_stream

    def synthesize(self, text: str, language: str = "mr") -> bytes:
        if not text or not text.strip():
            raise ValueError("Text for synthesis cannot be empty")

        clean_lang = language.lower().strip()
        if clean_lang not in self.VOICE_MAP:
            raise ValueError(f"Unsupported language code '{language}'. Allowed: {list(self.VOICE_MAP.keys())}")
        voice = self.VOICE_MAP[clean_lang]
        logger.info(f"[TTS_REQUEST_STARTED] language={clean_lang} voice={voice} text_length={len(text)}")

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                audio_bytes = pool.submit(asyncio.run, self._synthesize_async(text, voice)).result()
        else:
            audio_bytes = asyncio.run(self._synthesize_async(text, voice))

        if not audio_bytes or len(audio_bytes) < 100:
            raise RuntimeError(f"Edge TTS returned empty or incomplete audio stream for {clean_lang}")

        logger.info(f"[TTS_RESPONSE_RECEIVED] provider=edge-tts bytes={len(audio_bytes)}")
        return audio_bytes


class GTTSSpeechProvider(BaseTTSProvider):
    """
    Google Text-to-Speech (gTTS) secondary fallback provider.
    Runs reliably on standard HTTP endpoints without API credentials.
    """
    LANG_MAP: Dict[str, str] = {
        "mr": "mr",
        "hi": "hi",
        "en": "en",
    }

    def synthesize(self, text: str, language: str = "mr") -> bytes:
        if not text or not text.strip():
            raise ValueError("Text for synthesis cannot be empty")

        clean_lang = language.lower().strip()
        if clean_lang not in self.LANG_MAP:
            raise ValueError(f"Unsupported language code '{language}'. Allowed: {list(self.LANG_MAP.keys())}")
        gtts_lang = self.LANG_MAP[clean_lang]
        logger.info(f"[TTS_FALLBACK_STARTED] provider=gTTS language={gtts_lang} text_length={len(text)}")

        from gtts import gTTS
        buf = io.BytesIO()
        tts = gTTS(text=text.strip(), lang=gtts_lang, slow=False)
        tts.write_to_fp(buf)
        audio_bytes = buf.getvalue()

        if not audio_bytes or len(audio_bytes) < 100:
            raise RuntimeError(f"gTTS returned empty audio stream for {clean_lang}")

        logger.info(f"[TTS_FALLBACK_SUCCESS] provider=gTTS bytes={len(audio_bytes)}")
        return audio_bytes


class ProductionTTSProvider(BaseTTSProvider):
    """
    Composite provider:
    1. Primary: EdgeNeuralTTSProvider (high-fidelity neural Indian voices)
    2. Secondary fallback: GTTSSpeechProvider (Google multilingual TTS)
    """
    def __init__(self):
        self.edge_provider = EdgeNeuralTTSProvider()
        self.gtts_provider = GTTSSpeechProvider()

    def synthesize(self, text: str, language: str = "mr") -> bytes:
        if not text or not text.strip():
            raise ValueError("Text for synthesis cannot be empty")

        try:
            return self.edge_provider.synthesize(text, language)
        except Exception as e:
            logger.warning(f"[TTS_PRIMARY_FAILED] Edge TTS error: {e}. Switching to gTTS fallback.")
            try:
                return self.gtts_provider.synthesize(text, language)
            except Exception as e2:
                logger.error(f"[TTS_ERROR] All TTS providers failed: {e2}")
                raise RuntimeError(f"Voice synthesis failed for language '{language}': {e2}")
