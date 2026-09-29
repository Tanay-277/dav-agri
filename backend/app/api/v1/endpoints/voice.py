import base64
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Response, Query, Depends, status
from sqlalchemy.orm import Session
from app.services.voice_service import VoiceService
from app.services.query_service import QueryService
from app.schemas.common import APIResponse
from app.schemas.voice import TranscribeResponse, SynthesizeRequest, VoiceSampleResponse, VoiceQueryResponse
from app.schemas.query import QueryRequest
from app.api.deps import get_db, get_optional_user_id

router = APIRouter(prefix="/voice", tags=["Voice (STT & TTS)"])

@router.post("/transcribe", response_model=APIResponse[TranscribeResponse])
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = Form("mr")
):
    service = VoiceService()
    try:
        content = await file.read()
        result = service.transcribe_audio(content, language=language)
        return APIResponse.ok(result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Transcription failed: {str(e)}")

@router.post("/query", response_model=APIResponse[VoiceQueryResponse])
async def voice_query(
    file: UploadFile = File(...),
    language: str = Form("mr"),
    synthesize_response: bool = Form(True),
    db: Session = Depends(get_db),
    user_id: Optional[str] = Depends(get_optional_user_id)
):
    """
    Unified voice endpoint:
    1. Transcribes incoming audio (STT).
    2. Passes transcription through deterministic analytics & AI explanation.
    3. Synthesizes spoken audio explanation (TTS).
    4. Returns unified transcription, structured visual data, and audio payload.
    """
    effective_user_id = user_id or "user_demo_01"
    voice_service = VoiceService()
    query_service = QueryService(db)

    try:
        content = await file.read()
        transcription = voice_service.transcribe_audio(content, language=language)
        
        # Execute query intelligence
        query_req = QueryRequest(text=transcription.text, language=language)
        query_res = query_service.process_query(effective_user_id, query_req)

        audio_base64 = None
        if synthesize_response and query_res.answer:
            try:
                audio_bytes = voice_service.synthesize_speech(query_res.answer, language=language)
                audio_base64 = base64.b64encode(audio_bytes).decode("ascii")
            except Exception:
                audio_base64 = None

        return APIResponse.ok(VoiceQueryResponse(
            transcription=transcription,
            query_response=query_res,
            audio_base64=audio_base64
        ))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Voice query processing failed: {str(e)}")

@router.post("/synthesize")
def synthesize_speech(payload: SynthesizeRequest):
    service = VoiceService()
    try:
        audio_bytes = service.synthesize_speech(payload.text, language=payload.language)
        media_type = "audio/wav" if audio_bytes.startswith(b"RIFF") else "audio/mpeg"
        filename = "speech.wav" if media_type == "audio/wav" else "speech.mp3"
        return Response(
            content=audio_bytes,
            media_type=media_type,
            headers={
                "Content-Disposition": f"inline; filename={filename}",
                "Cache-Control": "no-cache"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Synthesis failed: {str(e)}")

@router.get("/sample", response_model=APIResponse[VoiceSampleResponse])
def get_language_sample(response: Response, language: str = Query("mr", pattern="^(en|hi|mr)$")):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    service = VoiceService()
    sample = service.get_sample_for_language(language)
    return APIResponse.ok(sample)
