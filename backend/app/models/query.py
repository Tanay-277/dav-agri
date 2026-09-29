import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.database.session import Base

class QueryHistory(Base):
    __tablename__ = "query_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    query_text = Column(Text, nullable=False)
    query_language = Column(String(10), nullable=False, default="mr")
    intent = Column(String(50), nullable=True)
    answer_text = Column(Text, nullable=False)
    visualization_data = Column(Text, nullable=True)  # JSON-encoded chart structure
    audio_url = Column(String(255), nullable=True)
    is_saved = Column(Boolean, default=False)
    share_token = Column(String(64), unique=True, nullable=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    user = relationship("User", back_populates="queries")

class WeatherCache(Base):
    __tablename__ = "weather_cache"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    location_key = Column(String(100), unique=True, nullable=False, index=True)
    cached_data = Column(Text, nullable=False)
    expires_at = Column(DateTime, nullable=False)
