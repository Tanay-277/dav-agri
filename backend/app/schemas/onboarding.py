from typing import Optional
from pydantic import BaseModel, Field

class OnboardingStatusResponse(BaseModel):
    user_id: str
    preferred_language: str = "mr"
    voice_confirmed: bool = False
    onboarding_completed: bool = False

class ConfirmLanguageRequest(BaseModel):
    language: str = Field(..., pattern="^(en|hi|mr)$", description="Supported language code: en, hi, mr")

class UpdateOnboardingRequest(BaseModel):
    preferred_language: Optional[str] = Field(None, pattern="^(en|hi|mr)$")
    voice_confirmed: Optional[bool] = None
    onboarding_completed: Optional[bool] = None
