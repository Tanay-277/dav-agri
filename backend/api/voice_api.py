from __future__ import annotations

from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field

from analytics import engine as kpi_engine
from api.routes import _as_filter_dict
from core.config import get_settings
from core.logging import get_logger
from database import data
from insights import engine as insight_engine
from models.schemas import DashboardFilters, Insight
from nlu.engine import QueryUnderstandingEngine
from nlu.schema import StructuredQuery
from speech_to_text.integration import SpeechToTextEngine
from speech_to_text.languages import SUPPORTED_LANGUAGES
from speech_to_text.provider import get_speech_provider
from text_to_speech.engine import TextToSpeechEngine
from text_to_speech.provider import get_tts_provider
from text_to_speech.schemas import VoiceGender

logger = get_logger(__name__)

router = APIRouter()

_nlu_engine = QueryUnderstandingEngine()


# ---------------------------------------------------------------------------
# Health / Status
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str
    version: str
    dataset_loaded: bool
    dataset_rows: int
    supported_languages: list[str]
    stt_providers: list[str]
    tts_providers: list[str]


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    df = data.get_dataset()
    stt_providers = []
    tts_providers = []
    try:
        stt_providers = get_speech_provider().__class__.__name__
    except Exception:
        pass
    try:
        tts_providers = get_tts_provider().__class__.__name__
    except Exception:
        pass
    return HealthResponse(
        status="ok",
        version="0.1.0",
        dataset_loaded=not df.empty,
        dataset_rows=int(len(df)),
        supported_languages=list(SUPPORTED_LANGUAGES.keys()),
        stt_providers=[stt_providers] if stt_providers else [],
        tts_providers=[tts_providers] if tts_providers else [],
    )


# ---------------------------------------------------------------------------
# Locations
# ---------------------------------------------------------------------------

class LocationResponse(BaseModel):
    states: list[str]
    districts: list[str]
    crops: list[str]


@router.get("/locations", response_model=LocationResponse)
def get_locations() -> LocationResponse:
    opts = data.get_filter_options()
    return LocationResponse(
        states=opts.get("state", []),
        districts=opts.get("district", []),
        crops=opts.get("crop", []),
    )


# ---------------------------------------------------------------------------
# Weather / Forecast
# ---------------------------------------------------------------------------

@router.get("/weather")
def get_weather(
    crop: str | None = None,
    state: str | None = None,
    district: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict:
    filters = DashboardFilters(crop=crop, state=state, district=district, start_date=start_date, end_date=end_date)
    df = data.get_filtered(_as_filter_dict(filters))
    kpis = kpi_engine.compute_kpis(df)
    return {
        "filters": _as_filter_dict(filters),
        "kpis": [k.model_dump() for k in kpis],
        "rows": int(len(df)),
    }


@router.get("/forecast")
def get_forecast(
    crop: str | None = None,
    state: str | None = None,
    district: str | None = None,
    days: int = Query(7, ge=1, le=30),
) -> dict:
    filters = DashboardFilters(crop=crop, state=state, district=district)
    df = data.get_filtered(_as_filter_dict(filters))
    kpis = kpi_engine.compute_kpis(df)
    return {
        "filters": _as_filter_dict(filters),
        "kpis": [k.model_dump() for k in kpis],
        "forecast_days": days,
    }


# ---------------------------------------------------------------------------
# Natural-language query
# ---------------------------------------------------------------------------

class TextQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural-language query text")
    language: str = Field(default="en", description="BCP-47 language code")
    context: dict[str, Any] | None = Field(default=None, description="Conversation context")


class QueryResponse(BaseModel):
    structured_query: StructuredQuery
    insights: list[Insight]
    speech_response: Any | None = None
    message: str = ""


@router.post("/query", response_model=QueryResponse)
def text_query(request: TextQueryRequest) -> QueryResponse:
    structured = _nlu_engine.parse(request.query, context=request.context or {})
    filters = _structured_query_to_filters(structured)
    df = data.get_filtered(filters) if any(filters.values()) else data.get_dataset()
    insights = insight_engine.generate_insights(df)
    return QueryResponse(
        structured_query=structured,
        insights=insights,
        message=f"Processed query: {request.query}",
    )


# ---------------------------------------------------------------------------
# Voice query (audio upload)
# ---------------------------------------------------------------------------

class VoiceQueryResponse(BaseModel):
    structured_query: StructuredQuery
    transcript: str
    normalized_transcript: str
    stt_confidence: float
    insights: list[Insight]
    speech_response: Any | None = None
    message: str = ""


@router.post("/voice-query", response_model=VoiceQueryResponse)
async def voice_query(
    audio: UploadFile = File(..., description="Audio file"),
    language: str = Form(default="en"),
    auto_detect: bool = Form(default=False),
    noise_level: str = Form(default="clean"),
) -> VoiceQueryResponse:
    stt_engine = SpeechToTextEngine()
    audio_bytes = await audio.read()
    stt_result = await stt_engine.process_audio(
        audio_bytes=audio_bytes,
        language=language,
        auto_detect=auto_detect,
        noise_level=noise_level,
        nlu_engine=_nlu_engine,
    )
    if not stt_result["success"]:
        raise HTTPException(status_code=400, detail=stt_result.get("error", "STT failed"))

    structured = stt_result["nlu_result"] or StructuredQuery(intent="general_query", raw_query=stt_result["transcript"])
    filters = _structured_query_to_filters(structured)
    df = data.get_filtered(filters) if any(filters.values()) else data.get_dataset()
    insights = insight_engine.generate_insights(df)
    return VoiceQueryResponse(
        structured_query=structured,
        transcript=stt_result["transcript"],
        normalized_transcript=stt_result["normalized_transcript"],
        stt_confidence=stt_result["confidence"],
        insights=insights,
        message="Voice query processed",
    )


# ---------------------------------------------------------------------------
# Structured insight
# ---------------------------------------------------------------------------

@router.get("/insight", response_model=list[Insight])
def get_insight(
    crop: str | None = None,
    state: str | None = None,
    district: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[Insight]:
    filters = DashboardFilters(crop=crop, state=state, district=district, start_date=start_date, end_date=end_date)
    df = data.get_filtered(_as_filter_dict(filters))
    return insight_engine.generate_insights(df)


# ---------------------------------------------------------------------------
# Speech response
# ---------------------------------------------------------------------------

class SpeechResponseRequest(BaseModel):
    insight: dict[str, Any] = Field(..., description="Structured insight JSON")
    language: str = Field(default="en")
    voice_gender: VoiceGender = Field(default=VoiceGender.FEMALE)
    rate: float = Field(default=1.0, ge=0.5, le=2.0)
    provider_name: str | None = Field(default=None, description="Override TTS provider name (test only)")


class SpeechResponse(BaseModel):
    text: str
    language: str
    audio_url: str | None = None
    audio_bytes: bytes | None = None
    content_type: str = "audio/mpeg"
    duration_ms: int = 0
    provider: str = ""
    success: bool = True
    message: str = ""


@router.post("/speech-response")
async def speech_response(request: SpeechResponseRequest) -> Response:
    from text_to_speech.provider import get_tts_provider

    provider_name = request.provider_name or get_settings().TTS_PROVIDER

    if provider_name == "mock" and not get_settings().TTS_ALLOW_MOCK:
        raise HTTPException(
            status_code=500,
            detail="Mock TTS provider is not allowed in production. "
                   "Set TTS_ALLOW_MOCK=true to enable mock provider.",
        )

    try:
        provider = get_tts_provider(provider_name)
    except ValueError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"TTS provider '{provider_name}' is not configured. "
                   f"Set TTS_PROVIDER env var or install the required dependency.",
        ) from exc

    if provider_name == "edge" and not getattr(provider, "_available", False):
        raise HTTPException(
            status_code=500,
            detail="EdgeTTS provider is not available. Install edge-tts: pip install edge-tts",
        )

    tts_engine = TextToSpeechEngine.__new__(TextToSpeechEngine)
    tts_engine.provider_name = provider_name
    tts_engine._provider = provider

    localized = tts_engine.generate_response(request.insight, language=request.language)
    synthesis = await tts_engine.synthesize_response(
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
                "message": synthesis.message or "Speech synthesis failed",
            },
        )

    return Response(
        content=synthesis.audio_bytes,
        media_type=synthesis.content_type or "audio/mpeg",
        headers={
            "X-Audio-Duration-Ms": str(synthesis.duration_ms),
            "X-Audio-Provider": synthesis.provider,
            "X-Audio-Language": localized.language,
            "X-Audio-Text": localized.text,
        },
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _structured_query_to_filters(query: StructuredQuery) -> dict[str, str | None]:
    return {
        "crop": query.entities.get("crop"),
        "state": query.entities.get("state"),
        "district": query.entities.get("district"),
        "start_date": query.time_period.start if query.time_period else None,
        "end_date": query.time_period.end if query.time_period else None,
    }
