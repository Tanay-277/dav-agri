from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.deps import get_current_user_id
from app.services.onboarding_service import OnboardingService
from app.schemas.common import APIResponse
from app.schemas.onboarding import (
    OnboardingStatusResponse,
    ConfirmLanguageRequest,
    UpdateOnboardingRequest,
)

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])

@router.get("/status", response_model=APIResponse[OnboardingStatusResponse])
def get_onboarding_status(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    service = OnboardingService(db)
    try:
        status_data = service.get_status(user_id)
        return APIResponse.ok(status_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/confirm-language", response_model=APIResponse[OnboardingStatusResponse])
def confirm_language(
    payload: ConfirmLanguageRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = OnboardingService(db)
    try:
        updated = service.confirm_language(user_id, payload.language)
        return APIResponse.ok(updated)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("", response_model=APIResponse[OnboardingStatusResponse])
def update_onboarding(
    payload: UpdateOnboardingRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = OnboardingService(db)
    try:
        updated = service.update_onboarding(user_id, payload)
        return APIResponse.ok(updated)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
