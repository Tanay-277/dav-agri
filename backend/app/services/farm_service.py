from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.farm_repo import FarmRepository
from app.repositories.user_repo import UserRepository
from app.schemas.farm import (
    CropRead,
    ProductionRecordCreate,
    ProductionRecordRead,
    ExpenseRecordCreate,
    ExpenseRecordRead,
    FarmSummaryResponse,
)

class FarmService:
    def __init__(self, db: Session):
        self.db = db
        self.farm_repo = FarmRepository(db)
        self.user_repo = UserRepository(db)

    def list_crops(self) -> List[CropRead]:
        crops = self.farm_repo.list_crops()
        return [
            CropRead(
                id=c.id,
                name_en=c.name_en,
                name_hi=c.name_hi,
                name_mr=c.name_mr,
                season=c.season,
                is_default=bool(c.is_default)
            )
            for c in crops
        ]

    def add_production_record(self, user_id: str, data: ProductionRecordCreate) -> ProductionRecordRead:
        crop = self.farm_repo.get_crop_by_id(data.crop_id)
        if not crop:
            raise ValueError(f"Crop with ID {data.crop_id} not found")

        record = self.farm_repo.add_production_record(
            user_id=user_id,
            crop_id=data.crop_id,
            year=data.year,
            quantity_quintals=data.quantity_quintals,
            revenue_inr=data.revenue_inr or 0.0,
            month=data.month,
            notes=data.notes
        )
        return ProductionRecordRead(
            id=record.id,
            user_id=record.user_id,
            crop_id=record.crop_id,
            crop_name=crop.name_mr,
            year=record.year,
            month=record.month,
            quantity_quintals=record.quantity_quintals,
            revenue_inr=record.revenue_inr,
            notes=record.notes,
            created_at=record.created_at
        )

    def list_production(self, user_id: str, crop_id: Optional[str] = None) -> List[ProductionRecordRead]:
        records = self.farm_repo.list_production_by_user(user_id, crop_id)
        result = []
        for r in records:
            crop_name = r.crop.name_mr if r.crop else "पीक"
            result.append(
                ProductionRecordRead(
                    id=r.id,
                    user_id=r.user_id,
                    crop_id=r.crop_id,
                    crop_name=crop_name,
                    year=r.year,
                    month=r.month,
                    quantity_quintals=r.quantity_quintals,
                    revenue_inr=r.revenue_inr,
                    notes=r.notes,
                    created_at=r.created_at
                )
            )
        return result

    def add_expense_record(self, user_id: str, data: ExpenseRecordCreate) -> ExpenseRecordRead:
        record = self.farm_repo.add_expense_record(
            user_id=user_id,
            category=data.category,
            amount_inr=data.amount_inr,
            crop_id=data.crop_id,
            notes=data.notes
        )
        return ExpenseRecordRead(
            id=record.id,
            user_id=record.user_id,
            crop_id=record.crop_id,
            category=record.category,
            amount_inr=record.amount_inr,
            expense_date=record.expense_date,
            notes=record.notes,
            created_at=record.created_at
        )

    def list_expenses(self, user_id: str, crop_id: Optional[str] = None) -> List[ExpenseRecordRead]:
        records = self.farm_repo.list_expenses_by_user(user_id, crop_id)
        return [
            ExpenseRecordRead(
                id=r.id,
                user_id=r.user_id,
                crop_id=r.crop_id,
                category=r.category,
                amount_inr=r.amount_inr,
                expense_date=r.expense_date,
                notes=r.notes,
                created_at=r.created_at
            )
            for r in records
        ]

    def get_summary(self, user_id: str) -> FarmSummaryResponse:
        profile = self.user_repo.get_profile(user_id)
        primary_crop = profile.primary_crop if profile else "Cotton"
        land_size = profile.land_size if profile else "20 acres"

        prod_records = self.list_production(user_id)
        total_prod = sum(p.quantity_quintals for p in prod_records)

        exp_records = self.list_expenses(user_id)
        total_exp = sum(e.amount_inr for e in exp_records)

        crops = self.list_crops()

        return FarmSummaryResponse(
            primary_crop=primary_crop,
            total_land_size=land_size,
            total_production_quintals=round(total_prod, 2),
            total_expenses_inr=round(total_exp, 2),
            active_crops=crops[:4],
            recent_records=prod_records[-5:]
        )
