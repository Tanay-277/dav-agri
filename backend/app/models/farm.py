import uuid
from datetime import datetime, date, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, Date, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.database.session import Base

class Crop(Base):
    __tablename__ = "crops"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name_en = Column(String(50), nullable=False)
    name_hi = Column(String(50), nullable=False)
    name_mr = Column(String(50), nullable=False)
    season = Column(String(50), nullable=True)  # Kharif / Rabi / Zaid
    is_default = Column(Boolean, default=False)

    production_records = relationship("ProductionRecord", back_populates="crop")
    expense_records = relationship("ExpenseRecord", back_populates="crop")

class ProductionRecord(Base):
    __tablename__ = "production_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    crop_id = Column(String(36), ForeignKey("crops.id"), nullable=False)
    year = Column(Integer, nullable=False, index=True)
    month = Column(Integer, nullable=True)
    quantity_quintals = Column(Float, nullable=False)
    revenue_inr = Column(Float, nullable=False, default=0.0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="production_records")
    crop = relationship("Crop", back_populates="production_records")

class ExpenseRecord(Base):
    __tablename__ = "expense_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    crop_id = Column(String(36), ForeignKey("crops.id"), nullable=True)
    category = Column(String(50), nullable=False, index=True)  # "labor", "seeds", "fertilizer", "pesticides", "other"
    amount_inr = Column(Float, nullable=False)
    expense_date = Column(Date, nullable=False, default=date.today)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="expense_records")
    crop = relationship("Crop", back_populates="expense_records")
