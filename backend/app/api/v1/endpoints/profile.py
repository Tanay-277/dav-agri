from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.deps import get_current_user_id
from app.services.profile_service import ProfileService
from app.schemas.common import APIResponse
from app.schemas.profile import ProfileRead, ProfileUpdate

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.get("", response_model=APIResponse[ProfileRead])
def get_profile(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    service = ProfileService(db)
    try:
        profile = service.get_profile(user_id)
        return APIResponse.ok(profile)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.put("", response_model=APIResponse[ProfileRead])
def update_profile(
    payload: ProfileUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = ProfileService(db)
    try:
        updated = service.update_profile(user_id, payload)
        return APIResponse.ok(updated)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
