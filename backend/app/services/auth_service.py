import logging
from typing import Optional
from sqlalchemy.orm import Session
from app.core.security import create_access_token, hash_password, verify_password
from app.services.google_auth_service import GoogleAuthService
from app.repositories.user_repo import UserRepository
from app.schemas.auth import TokenResponse, CurrentUserResponse

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def register(self, username: str, password: str) -> TokenResponse:
        username = username.strip()
        if self.user_repo.get_by_username(username) or self.user_repo.get_by_phone(username):
            raise ValueError("Username or phone number already registered")

        password_hash = hash_password(password)
        is_phone = username.isdigit()
        user = self.user_repo.create_user(
            phone=username if is_phone else None,
            username=None if is_phone else username,
            password_hash=password_hash,
        )

        onboarding = self.user_repo.get_onboarding(user.id)
        is_completed = bool(onboarding and onboarding.onboarding_completed)
        lang = onboarding.preferred_language if onboarding else "mr"

        token = create_access_token({"sub": user.id, "username": username, "lang": lang})
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user_id=user.id,
            phone=user.phone,
            onboarding_completed=is_completed,
            preferred_language=lang,
        )

    def login(self, username: str, password: str) -> TokenResponse:
        username = username.strip()
        user = self.user_repo.get_by_username(username) or self.user_repo.get_by_phone(username)
        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Invalid username or password")

        onboarding = self.user_repo.get_onboarding(user.id)
        is_completed = bool(onboarding and onboarding.onboarding_completed)
        lang = onboarding.preferred_language if onboarding else "mr"

        token = create_access_token({"sub": user.id, "username": username, "lang": lang})
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user_id=user.id,
            phone=user.phone,
            onboarding_completed=is_completed,
            preferred_language=lang,
        )

    def authenticate_google(self, id_token_str: str) -> TokenResponse:
        google_info = GoogleAuthService.verify_id_token(id_token_str)
        google_id = google_info["google_id"]

        user = self.user_repo.get_by_google_id(google_id)
        if not user:
            email_username = google_info.get("email")
            user = self.user_repo.create_user(google_id=google_id, username=email_username)
            if google_info.get("name"):
                self.user_repo.upsert_profile(user_id=user.id, name=google_info["name"])

        onboarding = self.user_repo.get_onboarding(user.id)
        is_completed = bool(onboarding and onboarding.onboarding_completed)
        lang = onboarding.preferred_language if onboarding else "mr"

        token = create_access_token({"sub": user.id, "google_id": user.google_id, "lang": lang})
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user_id=user.id,
            phone=user.phone,
            onboarding_completed=is_completed,
            preferred_language=lang,
        )

    def get_current_user_info(self, user_id: str) -> CurrentUserResponse:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        profile = self.user_repo.get_profile(user_id)
        onboarding = self.user_repo.get_onboarding(user_id)
        return CurrentUserResponse(
            user_id=user.id,
            username=user.username,
            phone=user.phone,
            google_id=user.google_id,
            name=profile.name if profile else "Raj Patil",
            preferred_language=onboarding.preferred_language if onboarding else "mr",
            onboarding_completed=onboarding.onboarding_completed if onboarding else False,
        )