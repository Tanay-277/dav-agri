from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field

from core.config import get_settings
from core.logging import get_logger
from text_to_speech.languages import (
    SUPPORTED_LANGUAGES,
    UNSUPPORTED_LANGUAGE_ERROR,
    is_language_supported,
)
from text_to_speech.provider import (
    EdgeTTSProvider,
    MockTTSProvider,
    get_tts_provider,
    register_tts_provider,
)
from text_to_speech.schemas import (
    LocalizedResponse,
    SynthesisRequest,
    VoiceGender,
)

logger = get_logger(__name__)
router = APIRouter()

_settings = get_settings()


def _register_configured_providers() -> None:
    provider_name = _settings.TTS_PROVIDER

    if provider_name == "mock":
        if not _settings.TTS_ALLOW_MOCK:
            raise RuntimeError(
                "Mock TTS provider is not allowed in production. "
                "Set TTS_ALLOW_MOCK=true to enable mock provider."
            )
        register_tts_provider(MockTTSProvider())
        logger.info("Registered TTS provider: mock (test mode)")
        return

    if provider_name == "edge":
        provider = EdgeTTSProvider()
        if not provider._available:
            raise RuntimeError(
                "EdgeTTS provider is configured but edge-tts is not installed. "
                "Install it with: pip install edge-tts"
            )
        register_tts_provider(provider)
        logger.info("Registered TTS provider: edge")
        if _settings.TTS_ALLOW_MOCK:
            register_tts_provider(MockTTSProvider())
            logger.info("Registered TTS provider: mock (test mode)")
        return

    raise ValueError(
        f"Unknown TTS provider: '{provider_name}'. "
        "Valid options: mock, edge."
    )


_register_configured_providers()


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


@router.post("/synthesize")
async def synthesize_insight(request: InsightRequest) -> Response:
    from text_to_speech.engine import TextToSpeechEngine
    engine = TextToSpeechEngine(provider_name=request.provider_name)
    synthesis = await engine.synthesize_response(
        request.insight,
        language=request.language,
        voice_gender=request.voice_gender,
        rate=request.rate,
    )
    if not synthesis.success or not synthesis.audio_bytes:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "provider": synthesis.provider,
                "message": synthesis.message or "Synthesis failed",
            },
        )
    return Response(
        content=synthesis.audio_bytes,
        media_type=synthesis.content_type or "audio/mpeg",
        headers={
            "X-Audio-Duration-Ms": str(synthesis.duration_ms),
            "X-Audio-Provider": synthesis.provider,
        },
    )


@router.post("/synthesize-text")
async def synthesize_text(
    text: str = Body(..., min_length=1, description="Text to synthesize"),
    language: str = Body(default="en"),
    voice_gender: VoiceGender = Body(default=VoiceGender.FEMALE),
    rate: float = Body(default=1.0, ge=0.5, le=2.0),
    provider_name: str | None = Body(default=None),
) -> Response:
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
        return JSONResponse(
            status_code=status_code,
            content={
                "success": False,
                "provider": response.provider,
                "message": response.message,
                "error": response.error.model_dump() if response.error else None,
            },
        )
    if not response.audio_bytes:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "provider": response.provider,
                "message": "No audio data returned",
            },
        )
    return Response(
        content=response.audio_bytes,
        media_type=response.content_type or "audio/mpeg",
        headers={
            "X-Audio-Duration-Ms": str(response.duration_ms),
            "X-Audio-Provider": response.provider,
        },
    )
