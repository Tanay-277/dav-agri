from typing import Optional
from pydantic import BaseModel, Field

class RequestOtpRequest(BaseModel):
    phone: str = Field(..., min_length=8, max_length=20, description="Farmer phone number")

class RequestOtpResponse(BaseModel):
    phone: str
    expires_in_seconds: int
    message: str

class VerifyOtpRequest(BaseModel):
    phone: str = Field(..., min_length=8, max_length=20)
    otp: str = Field(..., min_length=4, max_length=8)

class GoogleAuthRequest(BaseModel):
    id_token: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    phone: Optional[str] = None
    onboarding_completed: bool = False
    preferred_language: str = "mr"

class CurrentUserResponse(BaseModel):
    user_id: str
    phone: Optional[str] = None
    google_id: Optional[str] = None
    name: str = "Raj Patil"
    preferred_language: str = "mr"
    onboarding_completed: bool = False
