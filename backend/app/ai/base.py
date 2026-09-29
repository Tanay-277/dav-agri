from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseAIProvider(ABC):
    @property
    def provider_name(self) -> str:
        """Identifier for the AI provider engine ('gemini', 'mock')."""
        return "base"

    @abstractmethod
    def generate_explanation(
        self,
        prompt: str,
        verified_facts: Dict[str, Any],
        language: str = "mr"
    ) -> str:
        """Generate natural language explanation based strictly on verified numerical facts."""
        pass

    @abstractmethod
    def classify_intent(self, text: str) -> str:
        """Classify the user's agricultural voice or text query into an intent category."""
        pass
