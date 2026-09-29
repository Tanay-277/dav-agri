import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

class OnboardingPreference(Base):
    __tablename__ = "onboarding_preferences"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    preferred_language = Column(String(10), nullable=False, default="mr")  # "en", "hi", "mr"
    voice_confirmed = Column(Boolean, nullable=False, default=False)
    onboarding_completed = Column(Boolean, nullable=False, default=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="onboarding")
