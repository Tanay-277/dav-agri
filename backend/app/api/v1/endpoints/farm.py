from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.deps import get_current_user_id
from app.services.farm_service import FarmService
from app.services.analytics_service import AnalyticsService
from app.services.query_service import QueryService
from app.schemas.common import APIResponse
from app.schemas.farm import (
    CropRead,
    ProductionRecordCreate,
    ProductionRecordRead,
    ExpenseRecordCreate,
    ExpenseRecordRead,
    ExpenseBreakdownResponse,
    StructuredVisualization,
    FarmSummaryResponse,
)
from app.schemas.query import ConversationItem

router = APIRouter(prefix="/farm", tags=["Farm Operations & Analytics"])

@router.get("/crops", response_model=APIResponse[List[CropRead]])
def list_crops(db: Session = Depends(get_db)):
    service = FarmService(db)
    crops = service.list_crops()
    return APIResponse.ok(crops)

@router.get("/summary", response_model=APIResponse[FarmSummaryResponse])
def get_farm_summary(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    service = FarmService(db)
    summary = service.get_summary(user_id)
    return APIResponse.ok(summary)

@router.post("/production", response_model=APIResponse[ProductionRecordRead])
def add_production(
    payload: ProductionRecordCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = FarmService(db)
    try:
        record = service.add_production_record(user_id, payload)
        return APIResponse.ok(record)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/production", response_model=APIResponse[List[ProductionRecordRead]])
def list_production(
    crop_id: Optional[str] = Query(None),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = FarmService(db)
    records = service.list_production(user_id, crop_id)
    return APIResponse.ok(records)

@router.post("/expenses", response_model=APIResponse[ExpenseRecordRead])
def add_expense(
    payload: ExpenseRecordCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = FarmService(db)
    record = service.add_expense_record(user_id, payload)
    return APIResponse.ok(record)

@router.get("/expenses", response_model=APIResponse[List[ExpenseRecordRead]])
def list_expenses(
    crop_id: Optional[str] = Query(None),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = FarmService(db)
    records = service.list_expenses(user_id, crop_id)
    return APIResponse.ok(records)

@router.get("/expenses/breakdown", response_model=APIResponse[ExpenseBreakdownResponse])
def get_expense_breakdown(
    crop_id: Optional[str] = Query(None),
    language: str = Query("mr", pattern="^(en|hi|mr)$"),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    analytics = AnalyticsService(db)
    breakdown = analytics.calculate_expense_breakdown(user_id, crop_id, language=language)
    return APIResponse.ok(breakdown)

@router.get("/analytics/crop-income", response_model=APIResponse[StructuredVisualization])
def get_crop_income_chart(
    language: str = Query("mr", pattern="^(en|hi|mr)$"),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    analytics = AnalyticsService(db)
    chart = analytics.generate_crop_income_line_visualization(user_id, language=language)
    return APIResponse.ok(chart)

@router.get("/conversations", response_model=APIResponse[List[ConversationItem]])
def get_conversations(
    limit: int = Query(10, ge=1, le=50),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    query_service = QueryService(db)
    items = query_service.get_conversation_history(user_id, limit=limit)
    return APIResponse.ok(items)
