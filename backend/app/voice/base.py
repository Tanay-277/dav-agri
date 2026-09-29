from abc import ABC, abstractmethod
from typing import Tuple, Optional

class BaseSTTProvider(ABC):
    @abstractmethod
    def transcribe(self, audio_bytes: bytes, language: str = "mr") -> Tuple[str, float]:
        """
        Transcribe audio bytes to text.
        Returns (transcribed_text, confidence_score)
        """
        pass

class BaseTTSProvider(ABC):
    @abstractmethod
    def synthesize(self, text: str, language: str = "mr") -> bytes:
        """
        Synthesize text into audio bytes (e.g. WAV or MP3).
        """
        pass
