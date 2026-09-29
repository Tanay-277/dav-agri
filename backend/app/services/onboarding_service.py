from sqlalchemy.orm import Session
from app.repositories.user_repo import UserRepository
from app.schemas.onboarding import OnboardingStatusResponse, UpdateOnboardingRequest

class OnboardingService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def get_status(self, user_id: str) -> OnboardingStatusResponse:
        onboarding = self.user_repo.get_onboarding(user_id)
        if not onboarding:
            raise ValueError("Onboarding record not found")
        return OnboardingStatusResponse(
            user_id=onboarding.user_id,
            preferred_language=onboarding.preferred_language,
            voice_confirmed=onboarding.voice_confirmed,
            onboarding_completed=onboarding.onboarding_completed
        )

    def confirm_language(self, user_id: str, language_code: str) -> OnboardingStatusResponse:
        onboarding = self.user_repo.get_onboarding(user_id)
        if not onboarding:
            raise ValueError("Onboarding record not found")
        onboarding.preferred_language = language_code
        self.user_repo.update_onboarding(onboarding)
        return self.get_status(user_id)

    def update_onboarding(self, user_id: str, updates: UpdateOnboardingRequest) -> OnboardingStatusResponse:
        onboarding = self.user_repo.get_onboarding(user_id)
        if not onboarding:
            raise ValueError("Onboarding record not found")

        if updates.preferred_language is not None:
            onboarding.preferred_language = updates.preferred_language
        if updates.voice_confirmed is not None:
            onboarding.voice_confirmed = updates.voice_confirmed
        if updates.onboarding_completed is not None:
            onboarding.onboarding_completed = updates.onboarding_completed

        self.user_repo.update_onboarding(onboarding)
        return self.get_status(user_id)
