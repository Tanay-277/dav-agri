from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.weather_service import WeatherService
from app.schemas.common import APIResponse
from app.schemas.weather import AgriculturalWeatherResponse

router = APIRouter(prefix="/weather", tags=["Weather"])

@router.get("/current", response_model=APIResponse[AgriculturalWeatherResponse])
def get_current_weather(
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None),
    location: Optional[str] = Query(None),
    language: str = Query("mr", pattern="^(en|hi|mr)$"),
    db: Session = Depends(get_db)
):
    service = WeatherService(db)
    weather = service.get_agricultural_weather(lat=lat, lon=lon, location_name=location, language=language)
    return APIResponse.ok(weather)

@router.get("/forecast", response_model=APIResponse[AgriculturalWeatherResponse])
def get_forecast(
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None),
    location: Optional[str] = Query(None),
    language: str = Query("mr", pattern="^(en|hi|mr)$"),
    db: Session = Depends(get_db)
):
    service = WeatherService(db)
    forecast = service.get_agricultural_weather(lat=lat, lon=lon, location_name=location, language=language)
    return APIResponse.ok(forecast)
