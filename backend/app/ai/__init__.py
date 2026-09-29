from app.core.config import settings
from app.ai.base import BaseAIProvider
from app.ai.mock_provider import MockAIProvider
from app.ai.gemini_provider import GeminiAIProvider

def get_ai_provider() -> BaseAIProvider:
    """Factory returning GeminiAIProvider when GEMINI_API_KEY is configured,
    or MockAIProvider for offline / development testing.
    """
    if (settings.AI_PROVIDER == "gemini" or settings.GEMINI_API_KEY) and settings.GEMINI_API_KEY:
        return GeminiAIProvider(api_key=settings.GEMINI_API_KEY, model_name=settings.GEMINI_MODEL)
    return MockAIProvider()

__all__ = ["BaseAIProvider", "MockAIProvider", "GeminiAIProvider", "get_ai_provider"]
