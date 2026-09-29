from app.core.config import settings
from app.voice.base import BaseSTTProvider, BaseTTSProvider
from app.voice.providers import (
    MockSTTProvider,
    EdgeNeuralTTSProvider,
    GTTSSpeechProvider,
    ProductionTTSProvider,
)

def get_stt_provider() -> BaseSTTProvider:
    return MockSTTProvider()

def get_tts_provider() -> BaseTTSProvider:
    return ProductionTTSProvider()

__all__ = [
    "BaseSTTProvider",
    "BaseTTSProvider",
    "MockSTTProvider",
    "EdgeNeuralTTSProvider",
    "GTTSSpeechProvider",
    "ProductionTTSProvider",
    "get_stt_provider",
    "get_tts_provider",
]
