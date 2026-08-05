from __future__ import annotations

import json

from core.logging import get_logger

logger = get_logger(__name__)

try:
    from google import genai
except ImportError:  # pragma: no cover - optional dependency
    genai = None  # type: ignore[assignment]


class GeminiClient:
    """Thin wrapper around the Gemini API for narrative generation only.

    Only aggregate analytics (never raw datasets) are sent to the model.
    """

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash") -> None:
        if genai is None:
            raise RuntimeError(
                "google-genai is not installed. Add it to requirements.txt."
            )
        self.model = model
        self.client = genai.Client(api_key=api_key)

    def generate_story(
        self,
        summary: str,
        reasons: list[str],
        recommendations: list[str],
    ) -> str:
        payload = {
            "summary": summary,
            "reasons": reasons,
            "recommendations": recommendations,
        }
        prompt = (
            "You are an agricultural analyst. Convert the following analytics "
            "into a concise professional narrative for a farmer dashboard.\n\n"
            f"Data:\n{json.dumps(payload, indent=2)}\n\n"
            "Return a single polished paragraph (2-4 sentences) that summarises "
            "the situation, explains likely causes, and gives actionable advice. "
            "Do not mention JSON, raw numbers are fine but keep it human."
        )
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        return response.text.strip()
