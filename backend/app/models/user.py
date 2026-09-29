import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from app.database.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    phone = Column(String(20), unique=True, index=True, nullable=True)
    google_id = Column(String(100), unique=True, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    onboarding = relationship("OnboardingPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    production_records = relationship("ProductionRecord", back_populates="user", cascade="all, delete-orphan")
    expense_records = relationship("ExpenseRecord", back_populates="user", cascade="all, delete-orphan")
    queries = relationship("QueryHistory", back_populates="user", cascade="all, delete-orphan")
