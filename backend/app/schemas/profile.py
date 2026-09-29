from typing import List, Optional
from pydantic import BaseModel, Field

class ProfileBase(BaseModel):
    name: str = Field("Raj Patil", max_length=100)
    location: str = Field("Pune, MH", max_length=100)
    age: int = Field(42, ge=1, le=120)
    avatar_url: Optional[str] = None
    land_location: Optional[str] = Field("Plot No. 124/2, Kothrud", max_length=200)
    primary_crop: str = Field("Cotton", max_length=50)
    land_size: str = Field("20 acres", max_length=50)
    irrigation_type: str = Field("Rain Fed", max_length=50)
    livestock: Optional[str] = Field("Cow, Goat, Buffalo", max_length=150)
    crops_grown: List[str] = Field(default_factory=lambda: ["Cotton", "Wheat", "Ragi"])

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    age: Optional[int] = None
    avatar_url: Optional[str] = None
    land_location: Optional[str] = None
    primary_crop: Optional[str] = None
    land_size: Optional[str] = None
    irrigation_type: Optional[str] = None
    livestock: Optional[str] = None
    crops_grown: Optional[List[str]] = None
    preferred_language: Optional[str] = None

class ProfileRead(ProfileBase):
    id: str
    user_id: str
    preferred_language: str = "mr"
