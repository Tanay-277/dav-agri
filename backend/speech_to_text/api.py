from __future__ import annotations

import logging
import time
from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from speech_to_text.languages import (
    SUPPORTED_LANGUAGES,
    UNSUPPORTED_LANGUAGE_ERROR,
    get_language_config,
    is_language_supported,
)
from speech_to_text.provider import (
    MockSpeechProvider,
    WhisperSpeechProvider,
    get_speech_provider,
    register_speech_provider,
)
from speech_to_text.schemas import (
    AudioFormat,
    NoiseLevel,
    TranscriptionRequest,
    TranscriptionResponse,
)

from core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

try:
    register_speech_provider(WhisperSpeechProvider(model_size="small"))
except Exception as exc:
    logger.warning("Could not register Whisper provider: %s", exc)
register_speech_provider(MockSpeechProvider())


@router.get("/languages")
def list_supported_languages() -> dict[str, Any]:
    provider = get_speech_provider()
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


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    audio: UploadFile = File(..., description="Audio file to transcribe"),
    language: str = Form(default="en", description="BCP-47 language code"),
    auto_detect_language: bool = Form(default=False),
    noise_level: str = Form(default="clean"),
    enable_segmentation: bool = Form(default=True),
    provider_name: str | None = Form(default=None),
) -> TranscriptionResponse:
    if not is_language_supported(language):
        raise HTTPException(status_code=400, detail=UNSUPPORTED_LANGUAGE_ERROR)

    try:
        noise_enum = NoiseLevel(noise_level.lower())
    except ValueError:
        noise_enum = NoiseLevel.CLEAN

    request = TranscriptionRequest(
        language=language,
        auto_detect_language=auto_detect_language,
        noise_level=noise_enum,
        enable_segmentation=enable_segmentation,
    )

    try:
        provider = get_speech_provider(provider_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        audio_bytes = await audio.read()
    except Exception as exc:
        logger.error("Failed to read audio upload: %s", exc)
        raise HTTPException(status_code=400, detail="Failed to read uploaded audio.") from exc

    response = await provider.transcribe(audio_bytes, request)
    if not response.success:
        status_code = 422 if "no speech" in response.message.lower() else 400
        return JSONResponse(
            status_code=status_code,
            content=response.model_dump(),
        )
    return response
