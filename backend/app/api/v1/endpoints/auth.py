from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.deps import get_current_user_id
from app.services.auth_service import AuthService
from app.schemas.common import APIResponse
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    GoogleAuthRequest,
    TokenResponse,
    CurrentUserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=APIResponse[TokenResponse])
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    try:
        res = auth_service.register(payload.username, payload.password)
        return APIResponse.ok(res)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Registration failed")

@router.post("/login", response_model=APIResponse[TokenResponse])
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    try:
        res = auth_service.login(payload.username, payload.password)
        return APIResponse.ok(res)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed")

@router.post("/google", response_model=APIResponse[TokenResponse])
def google_auth(payload: GoogleAuthRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    try:
        res = auth_service.authenticate_google(payload.id_token)
        return APIResponse.ok(res)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/me", response_model=APIResponse[CurrentUserResponse])
def get_current_user(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    try:
        res = auth_service.get_current_user_info(user_id)
        return APIResponse.ok(res)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")