from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel, Field

from text_to_speech.languages import (
    SUPPORTED_LANGUAGES,
    UNSUPPORTED_LANGUAGE_ERROR,
    get_language_config,
    is_language_supported,
)
from text_to_speech.provider import (
    EdgeTTSProvider,
    MockTTSProvider,
    get_tts_provider,
    register_tts_provider,
)
from text_to_speech.schemas import (
    AudioFormat,
    InsightType,
    LocalizedResponse,
    SynthesisRequest,
    SynthesisResponse,
    VoiceGender,
)

from core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

try:
    register_tts_provider(EdgeTTSProvider())
except Exception as exc:
    logger.warning("Could not register EdgeTTS provider: %s", exc)
register_tts_provider(MockTTSProvider())


class InsightRequest(BaseModel):
    insight: dict[str, Any] = Field(..., description="Structured insight from analytics engine")
    language: str = Field(default="en", description="Target language code")
    voice_gender: VoiceGender = Field(default=VoiceGender.FEMALE)
    rate: float = Field(default=1.0, ge=0.5, le=2.0)
    provider_name: str | None = Field(default=None)


@router.get("/languages")
def list_supported_languages() -> dict[str, Any]:
    provider = get_tts_provider()
    supported = []
    for code, config in SUPPORTED_LANGUAGES.items():
        supported.append({
            "code": code,
            "name": config.name,
            "bcp47_tag": config.bcp47_tag,
            "provider_supported": provider.supports_language(code),
        })
    return {
        "supported_languages": supported,
        "default": "en",
    }


@router.post("/localize", response_model=LocalizedResponse)
def localize_insight(request: InsightRequest) -> LocalizedResponse:
    from text_to_speech.engine import TextToSpeechEngine
    engine = TextToSpeechEngine(provider_name=request.provider_name)
    return engine.generate_response(request.insight, language=request.language)


@router.post("/synthesize", response_model=SynthesisResponse)
async def synthesize_insight(request: InsightRequest) -> SynthesisResponse:
    from text_to_speech.engine import TextToSpeechEngine
    engine = TextToSpeechEngine(provider_name=request.provider_name)
    return await engine.synthesize_response(
        request.insight,
        language=request.language,
        voice_gender=request.voice_gender,
        rate=request.rate,
    )


@router.post("/synthesize-text", response_model=SynthesisResponse)
async def synthesize_text(
    text: str = Body(..., min_length=1, description="Text to synthesize"),
    language: str = Body(default="en"),
    voice_gender: VoiceGender = Body(default=VoiceGender.FEMALE),
    rate: float = Body(default=1.0, ge=0.5, le=2.0),
    provider_name: str | None = Body(default=None),
) -> SynthesisResponse:
    if not is_language_supported(language):
        raise HTTPException(status_code=400, detail=UNSUPPORTED_LANGUAGE_ERROR)
    try:
        provider = get_tts_provider(provider_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    request = SynthesisRequest(
        text=text,
        language=language,
        voice_gender=voice_gender,
        rate=rate,
    )
    response = await provider.synthesize(request)
    if not response.success:
        status_code = 422 if response.error and response.error.code == "empty_text" else 400
        return SynthesisResponse(
            success=False,
            provider=response.provider,
            message=response.message,
            error=response.error,
        )
    return response
