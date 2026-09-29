from typing import List, Optional, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel, Field

class CropRead(BaseModel):
    id: str
    name_en: str
    name_hi: str
    name_mr: str
    season: Optional[str] = None
    is_default: bool = False

class ProductionRecordCreate(BaseModel):
    crop_id: str
    year: int = Field(..., ge=1990, le=2050)
    month: Optional[int] = Field(None, ge=1, le=12)
    quantity_quintals: float = Field(..., gt=0)
    revenue_inr: Optional[float] = Field(0.0, ge=0)
    notes: Optional[str] = None

class ProductionRecordRead(BaseModel):
    id: str
    user_id: str
    crop_id: str
    crop_name: str
    year: int
    month: Optional[int]
    quantity_quintals: float
    revenue_inr: float
    notes: Optional[str]
    created_at: datetime

class ExpenseRecordCreate(BaseModel):
    crop_id: Optional[str] = None
    category: str = Field(..., pattern="^(labor|seeds|fertilizer|pesticides|other)$")
    amount_inr: float = Field(..., gt=0)
    expense_date: Optional[date] = None
    notes: Optional[str] = None

class ExpenseRecordRead(BaseModel):
    id: str
    user_id: str
    crop_id: Optional[str]
    category: str
    amount_inr: float
    expense_date: date
    notes: Optional[str]
    created_at: datetime

class ExpenseCategoryItem(BaseModel):
    category: str
    label_en: str
    label_hi: str
    label_mr: str
    amount_inr: float
    percentage: float
    color: str

class ExpenseBreakdownResponse(BaseModel):
    total_expense_inr: float
    breakdown: List[ExpenseCategoryItem]
    labels: List[str]
    percentages: List[float]
    colors: List[str]

class ChartDataset(BaseModel):
    name: str
    color: str
    data: List[float]

class StructuredVisualization(BaseModel):
    type: str  # "stacked_bar", "line", "donut", "pie"
    title: str
    unit: Optional[str] = None
    labels: List[str]
    datasets: List[ChartDataset]
    raw_data: Optional[Dict[str, Any]] = None

class FarmSummaryResponse(BaseModel):
    primary_crop: str
    total_land_size: str
    total_production_quintals: float
    total_expenses_inr: float
    active_crops: List[CropRead]
    recent_records: List[ProductionRecordRead]
