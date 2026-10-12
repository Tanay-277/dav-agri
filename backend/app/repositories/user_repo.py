from typing import Optional
from sqlalchemy.orm import Session
from app.core.security import hash_password
from app.models.user import User
from app.models.profile import Profile
from app.models.onboarding import OnboardingPreference

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_phone(self, phone: str) -> Optional[User]:
        return self.db.query(User).filter(User.phone == phone).first()

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def get_by_google_id(self, google_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.google_id == google_id).first()

    def create_user(
        self,
        phone: Optional[str] = None,
        google_id: Optional[str] = None,
        username: Optional[str] = None,
        password_hash: Optional[str] = None,
    ) -> User:
        user = User(phone=phone, google_id=google_id, username=username, password_hash=password_hash)
        self.db.add(user)
        self.db.flush()

        profile = Profile(
            user_id=user.id,
            name="Farmer" if not phone else f"Farmer {phone[-4:]}",
            location="Pune, MH",
            age=40,
            primary_crop="Cotton",
            land_size="10 acres",
            irrigation_type="Rain Fed",
            livestock="Cow, Buffalo",
            crops_grown='"["Cotton", "Wheat"]"'
        )
        self.db.add(profile)

        onboarding = OnboardingPreference(
            user_id=user.id,
            preferred_language="mr",
            voice_confirmed=False,
            onboarding_completed=False
        )
        self.db.add(onboarding)
        self.db.commit()
        self.db.refresh(user)
        return user

    def set_password(self, user: User, password_hash: str) -> User:
        user.password_hash = password_hash
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_profile(self, user_id: str) -> Optional[Profile]:
        return self.db.query(Profile).filter(Profile.user_id == user_id).first()

    def upsert_profile(self, user_id: str, name: str) -> Profile:
        profile = self.get_profile(user_id)
        if profile:
            profile.name = name
        else:
            profile = Profile(user_id=user_id, name=name)
        return self.update_profile(profile)

    def update_profile(self, profile: Profile) -> Profile:
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def get_onboarding(self, user_id: str) -> Optional[OnboardingPreference]:
        return self.db.query(OnboardingPreference).filter(OnboardingPreference.user_id == user_id).first()

    def update_onboarding(self, onboarding: OnboardingPreference) -> OnboardingPreference:
        self.db.add(onboarding)
        self.db.commit()
        self.db.refresh(onboarding)
        return onboarding