from typing import List, Optional
from pydantic import BaseModel

class TimeSlotForecast(BaseModel):
    period: str  # "morning", "afternoon", "evening", "night"
    label_en: str
    label_hi: str
    label_mr: str
    temp_c: float
    condition: str  # "sunny_cloud", "rain", "rain_sun", "cloud"
    rain_probability: int

class AgriculturalWeatherResponse(BaseModel):
    location: str
    temperature_c: float
    condition: str
    expected_rainfall_mm: float
    duration_hours: int
    intensity: str  # "light", "moderate", "heavy"
    intensity_level: int  # 1 to 4 droplets
    irrigation_needed: bool
    irrigation_advisory_en: str
    irrigation_advisory_hi: str
    irrigation_advisory_mr: str
    advisory: Optional[str] = None
    language: Optional[str] = "mr"
    is_live: bool = False
    source: str = "mock"
    time_slots: List[TimeSlotForecast]
