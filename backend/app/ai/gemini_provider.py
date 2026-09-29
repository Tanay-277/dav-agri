import logging
from typing import Dict, Any
import httpx
from app.ai.base import BaseAIProvider
from app.ai.mock_provider import MockAIProvider
from app.ai.prompts import get_system_prompt, get_explanation_prompt
from app.core.config import settings

logger = logging.getLogger(__name__)

class GeminiAIProvider(BaseAIProvider):
    """Google Gemini AI integration using direct REST API via httpx.
    Strictly grounds answers in verified agricultural facts and enforces
    the user's chosen language ('en', 'hi', 'mr').
    """

    def __init__(self, api_key: str = "", model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model_name or settings.GEMINI_MODEL
        self.fallback = MockAIProvider()

    @property
    def provider_name(self) -> str:
        return "gemini" if self.api_key else "mock"

    def classify_intent(self, text: str) -> str:
        if not self.api_key:
            return self.fallback.classify_intent(text)

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        prompt = (
            "Classify this farmer query into exactly one intent name from: "
            "production_trend, expense_breakdown, weather, crop_protection, crop_prices, government_schemes.\n"
            f"Query: {text}\n"
            "Reply strictly with only the single intent name in lowercase and no other words or punctuation."
        )

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.0,
                "maxOutputTokens": 20
            }
        }

        try:
            with httpx.Client(timeout=8.0) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts and "text" in parts[0]:
                            intent = parts[0]["text"].strip().lower()
                            if intent in [
                                "production_trend",
                                "expense_breakdown",
                                "weather",
                                "crop_protection",
                                "crop_prices",
                                "government_schemes",
                            ]:
                                return intent
                else:
                    logger.warning(
                        f"[GEMINI] Intent classification failed: HTTP {res.status_code} {res.text}. Falling back to mock."
                    )
        except Exception as e:
            logger.warning(f"[GEMINI] Intent classification network error: {e}. Falling back to mock.")

        return self.fallback.classify_intent(text)

    def generate_explanation(
        self,
        prompt: str,
        verified_facts: Dict[str, Any],
        language: str = "mr"
    ) -> str:
        clean_lang = language.lower().strip()
        if clean_lang not in ("en", "hi", "mr"):
            raise ValueError(f"Unsupported language code '{language}'. Must be one of ['en', 'hi', 'mr']")

        if not self.api_key:
            return self.fallback.generate_explanation(prompt, verified_facts, clean_lang)

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"

        sys_prompt = get_system_prompt(clean_lang)
        sys_prompt += (
            f"\nCRITICAL LOCALIZATION LOCK: You MUST write your ENTIRE response in language '{clean_lang}'. "
            "Do NOT mix in other languages. Ground every single claim strictly on the provided verified farm facts."
        )

        full_prompt = get_explanation_prompt("farm_analytics", verified_facts, clean_lang)
        full_prompt += f"\nFarmer Query: {prompt}"

        payload = {
            "system_instruction": {
                "parts": [{"text": sys_prompt}]
            },
            "contents": [
                {"parts": [{"text": full_prompt}]}
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 800
            }
        }

        try:
            with httpx.Client(timeout=8.0) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts and "text" in parts[0]:
                            text = parts[0]["text"].strip()
                            if text:
                                return text
                else:
                    logger.warning(
                        f"[GEMINI] Explanation generation error: HTTP {res.status_code} {res.text}. Falling back to verified mock generator."
                    )
        except Exception as e:
            logger.warning(f"[GEMINI] Explanation generation network error: {e}. Falling back to verified mock generator.")

        # Robust graceful fallback to deterministic verified generator
        return self.fallback.generate_explanation(prompt, verified_facts, clean_lang)
