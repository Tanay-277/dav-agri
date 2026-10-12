from typing import List, Optional, Dict
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
    
    # New optional fields for enhanced agricultural data
    soil_moisture_profile: Optional[Dict[str, float]] = None  # depth -> m³/m³
    soil_temperature_profile: Optional[Dict[str, float]] = None  # depth -> °C
    et0_mm: Optional[float] = None  # daily ET0 in mm
    vpd_kpa: Optional[float] = None  # vapor pressure deficit in kPa
    solar_radiation_w_m2: Optional[float] = None  # shortwave radiation in W/m²
    relative_humidity: Optional[float] = None  # %
    dew_point_c: Optional[float] = None  # °C
    apparent_temperature_c: Optional[float] = None  # °C
    wind_speed_ms: Optional[float] = None  # m/s
    wind_direction_deg: Optional[float] = None  # degrees
    wind_gusts_ms: Optional[float] = None  # m/s
    surface_pressure_hpa: Optional[float] = None  # hPa
    precipitation_probability: Optional[int] = None  # %
    weather_code: Optional[int] = None  # WMO code
    shortwave_radiation_w_m2: Optional[float] = None  # W/m²
    direct_radiation_w_m2: Optional[float] = None  # W/m²
    diffuse_radiation_w_m2: Optional[float] = None  # W/m²
