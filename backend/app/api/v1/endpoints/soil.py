from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.soil_service import SoilService
from app.schemas.common import APIResponse
from app.schemas.soil import SoilDataResponse

router = APIRouter(prefix="/soil", tags=["Soil"])

@router.get("/profile", response_model=APIResponse[SoilDataResponse])
def get_soil_profile(
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None),
    location: Optional[str] = Query(None),
    language: str = Query("mr", pattern="^(en|hi|mr)$"),
    db: Session = Depends(get_db)
):
    service = SoilService(db)
    soil = service.get_soil_data(lat=lat, lon=lon, location_name=location, language=language)
    return APIResponse.ok(soil)