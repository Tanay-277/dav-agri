import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import create_access_token
from app.otp import get_otp_provider
from app.services.google_auth_service import GoogleAuthService
from app.repositories.user_repo import UserRepository
from app.schemas.auth import (
    RequestOtpResponse,
    TokenResponse,
    CurrentUserResponse,
)

logger = logging.getLogger(__name__)

# In-memory OTP storage for development & production verification (keyed by phone)
_otp_store: Dict[str, Dict[str, Any]] = {}

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.otp_provider = get_otp_provider()

    def request_otp(self, phone: str) -> RequestOtpResponse:
        cleaned_phone = phone.strip().replace(" ", "").replace("-", "")
        
        # Generate OTP via active provider (Mock or Twilio)
        otp = self.otp_provider.generate_otp()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
        _otp_store[cleaned_phone] = {
            "otp": otp,
            "expires_at": expires_at
        }
        
        # Dispatch OTP via provider
        self.otp_provider.send_otp(cleaned_phone, otp)

        return RequestOtpResponse(
            phone=cleaned_phone,
            expires_in_seconds=300,
            message="OTP sent successfully"
        )

    def verify_otp(self, phone: str, otp: str) -> TokenResponse:
        cleaned_phone = phone.strip().replace(" ", "").replace("-", "")
        stored_data = _otp_store.get(cleaned_phone)

        # Verification check
        valid = False
        if settings.ENVIRONMENT == "development" and not self.otp_provider.is_production and otp == settings.DEV_MOCK_OTP:
            valid = True
        elif stored_data and stored_data["otp"] == otp:
            if datetime.now(timezone.utc) <= stored_data["expires_at"]:
                valid = True

        if not valid:
            raise ValueError("Invalid or expired OTP")

        # Clear used OTP
        if cleaned_phone in _otp_store:
            del _otp_store[cleaned_phone]

        # Get or create user
        user = self.user_repo.get_by_phone(cleaned_phone)
        if not user:
            user = self.user_repo.create_user(phone=cleaned_phone)

        onboarding = self.user_repo.get_onboarding(user.id)
        is_completed = onboarding.onboarding_completed if onboarding else False
        lang = onboarding.preferred_language if onboarding else "mr"

        token = create_access_token({
            "sub": user.id,
            "phone": user.phone,
            "lang": lang
        })

        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user_id=user.id,
            phone=user.phone,
            onboarding_completed=is_completed,
            preferred_language=lang
        )

    def authenticate_google(self, id_token_str: str) -> TokenResponse:
        # Verify via GoogleAuthService (TokenInfo API with dev fallback)
        google_info = GoogleAuthService.verify_id_token(id_token_str)
        google_id = google_info["google_id"]

        user = self.user_repo.get_by_google_id(google_id)
        if not user:
            user = self.user_repo.create_user(google_id=google_id)
            if google_info.get("name"):
                self.user_repo.upsert_profile(
                    user_id=user.id,
                    name=google_info["name"]
                )

        onboarding = self.user_repo.get_onboarding(user.id)
        is_completed = onboarding.onboarding_completed if onboarding else False
        lang = onboarding.preferred_language if onboarding else "mr"

        token = create_access_token({
            "sub": user.id,
            "google_id": user.google_id,
            "lang": lang
        })

        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user_id=user.id,
            phone=user.phone,
            onboarding_completed=is_completed,
            preferred_language=lang
        )

    def get_current_user_info(self, user_id: str) -> CurrentUserResponse:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        profile = self.user_repo.get_profile(user_id)
        onboarding = self.user_repo.get_onboarding(user_id)

        return CurrentUserResponse(
            user_id=user.id,
            phone=user.phone,
            google_id=user.google_id,
            name=profile.name if profile else "Raj Patil",
            preferred_language=onboarding.preferred_language if onboarding else "mr",
            onboarding_completed=onboarding.onboarding_completed if onboarding else False
        )
