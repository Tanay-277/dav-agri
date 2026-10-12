from typing import Optional
from pydantic import BaseModel, Field

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Phone number or chosen username")
    password: str = Field(..., min_length=6, max_length=128, description="Login password")

class LoginRequest(BaseModel):
    username: str = Field(..., description="Phone number or username")
    password: str = Field(..., description="Login password")

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
    username: Optional[str] = None
    phone: Optional[str] = None
    google_id: Optional[str] = None
    name: str = "Raj Patil"
    preferred_language: str = "mr"
    onboarding_completed: bool = False