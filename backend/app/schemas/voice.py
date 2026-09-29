from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.query import QueryResponse

class TranscribeResponse(BaseModel):
    text: str
    confidence: float
    language: str
    duration_seconds: Optional[float] = None

class SynthesizeRequest(BaseModel):
    text: str = Field(..., min_length=1)
    language: str = Field("mr", pattern="^(en|hi|mr)$")
    voice_gender: Optional[str] = "neutral"

class VoiceSampleResponse(BaseModel):
    language: str
    sample_text: str
    audio_base64: str
    mime_type: Optional[str] = "audio/mpeg"

class VoiceQueryResponse(BaseModel):
    transcription: TranscribeResponse
    query_response: QueryResponse
    audio_base64: Optional[str] = None
