import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.session import Base

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    name = Column(String(100), nullable=False, default="Raj Patil")
    location = Column(String(100), nullable=False, default="Pune, MH")
    age = Column(Integer, nullable=False, default=42)
    avatar_url = Column(String(255), nullable=True)
    
    # Farm Details (Figma screen 17)
    land_location = Column(String(200), default="Plot No. 124/2, Kothrud")
    primary_crop = Column(String(50), default="Cotton")
    land_size = Column(String(50), default="20 acres")
    irrigation_type = Column(String(50), default="Rain Fed")
    livestock = Column(String(150), default="Cow, Goat, Buffalo")
    crops_grown = Column(Text, default='["Cotton", "Wheat", "Ragi"]')
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="profile")
