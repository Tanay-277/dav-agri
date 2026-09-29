import json
from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.user_repo import UserRepository
from app.schemas.profile import ProfileRead, ProfileUpdate

class ProfileService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def get_profile(self, user_id: str) -> ProfileRead:
        profile = self.user_repo.get_profile(user_id)
        if not profile:
            raise ValueError("Profile not found")

        onboarding = self.user_repo.get_onboarding(user_id)
        lang = onboarding.preferred_language if onboarding else "mr"

        crops_list = []
        if profile.crops_grown:
            try:
                crops_list = json.loads(profile.crops_grown)
            except Exception:
                crops_list = [c.strip() for c in profile.crops_grown.split(",") if c.strip()]

        return ProfileRead(
            id=profile.id,
            user_id=profile.user_id,
            name=profile.name,
            location=profile.location,
            age=profile.age,
            avatar_url=profile.avatar_url,
            land_location=profile.land_location,
            primary_crop=profile.primary_crop,
            land_size=profile.land_size,
            irrigation_type=profile.irrigation_type,
            livestock=profile.livestock,
            crops_grown=crops_list,
            preferred_language=lang
        )

    def update_profile(self, user_id: str, updates: ProfileUpdate) -> ProfileRead:
        profile = self.user_repo.get_profile(user_id)
        if not profile:
            raise ValueError("Profile not found")

        if updates.name is not None:
            profile.name = updates.name
        if updates.location is not None:
            profile.location = updates.location
        if updates.age is not None:
            profile.age = updates.age
        if updates.avatar_url is not None:
            profile.avatar_url = updates.avatar_url
        if updates.land_location is not None:
            profile.land_location = updates.land_location
        if updates.primary_crop is not None:
            profile.primary_crop = updates.primary_crop
        if updates.land_size is not None:
            profile.land_size = updates.land_size
        if updates.irrigation_type is not None:
            profile.irrigation_type = updates.irrigation_type
        if updates.livestock is not None:
            profile.livestock = updates.livestock
        if updates.crops_grown is not None:
            profile.crops_grown = json.dumps(updates.crops_grown)

        if updates.preferred_language is not None:
            if updates.preferred_language not in ["mr", "hi", "en"]:
                raise ValueError("Invalid language code. Supported: en, hi, mr")
            onboarding = self.user_repo.get_onboarding(user_id)
            if onboarding:
                onboarding.preferred_language = updates.preferred_language
                self.user_repo.update_onboarding(onboarding)

        updated_profile = self.user_repo.update_profile(profile)
        return self.get_profile(user_id)
