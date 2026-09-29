from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.farm import Crop, ProductionRecord, ExpenseRecord

class FarmRepository:
    def __init__(self, db: Session):
        self.db = db

    # Crops Catalog (Public / Shared)
    def list_crops(self) -> List[Crop]:
        return self.db.query(Crop).order_by(Crop.is_default.desc(), Crop.name_en.asc()).all()

    def get_crop_by_id(self, crop_id: str) -> Optional[Crop]:
        return self.db.query(Crop).filter(Crop.id == crop_id).first()

    def get_crop_by_name(self, name: str) -> Optional[Crop]:
        name_lower = name.strip().lower()
        return self.db.query(Crop).filter(
            (Crop.name_en.ilike(name_lower)) |
            (Crop.name_hi == name.strip()) |
            (Crop.name_mr == name.strip())
        ).first()

    # Production Records (Strictly user_id scoped)
    def list_production_by_user(self, user_id: str, crop_id: Optional[str] = None) -> List[ProductionRecord]:
        q = self.db.query(ProductionRecord).filter(ProductionRecord.user_id == user_id)
        if crop_id:
            q = q.filter(ProductionRecord.crop_id == crop_id)
        return q.order_by(ProductionRecord.year.asc(), ProductionRecord.month.asc()).all()

    def add_production_record(self, user_id: str, crop_id: str, year: int, quantity_quintals: float, revenue_inr: float = 0.0, month: Optional[int] = None, notes: Optional[str] = None) -> ProductionRecord:
        record = ProductionRecord(
            user_id=user_id,
            crop_id=crop_id,
            year=year,
            month=month,
            quantity_quintals=quantity_quintals,
            revenue_inr=revenue_inr,
            notes=notes
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    # Expense Records (Strictly user_id scoped)
    def list_expenses_by_user(self, user_id: str, crop_id: Optional[str] = None) -> List[ExpenseRecord]:
        q = self.db.query(ExpenseRecord).filter(ExpenseRecord.user_id == user_id)
        if crop_id:
            q = q.filter(ExpenseRecord.crop_id == crop_id)
        return q.order_by(ExpenseRecord.expense_date.desc()).all()

    def add_expense_record(self, user_id: str, category: str, amount_inr: float, crop_id: Optional[str] = None, notes: Optional[str] = None) -> ExpenseRecord:
        record = ExpenseRecord(
            user_id=user_id,
            category=category,
            amount_inr=amount_inr,
            crop_id=crop_id,
            notes=notes
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record
