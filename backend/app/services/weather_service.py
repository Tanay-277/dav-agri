import json
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.core.config import settings
from app.integrations.weather import get_weather_provider
from app.models.query import WeatherCache
from app.schemas.weather import AgriculturalWeatherResponse

class WeatherService:
    def __init__(self, db: Session):
        self.db = db
        self.provider = get_weather_provider()

    def get_agricultural_weather(
        self,
        lat: float = None,
        lon: float = None,
        location_name: str = None,
        language: str = "mr"
    ) -> AgriculturalWeatherResponse:
        clean_lang = language.lower().strip()
        if clean_lang not in ("en", "hi", "mr"):
            raise ValueError(f"Unsupported language code '{language}'. Must be one of ['en', 'hi', 'mr']")

        lat = lat if lat is not None else settings.DEFAULT_LATITUDE
        lon = lon if lon is not None else settings.DEFAULT_LONGITUDE
        loc_name = location_name or settings.DEFAULT_LOCATION_NAME

        cache_key = f"{round(lat, 2)}_{round(lon, 2)}"
        now = datetime.now(timezone.utc)

        # Check in-memory/DB cache
        weather_data: Optional[AgriculturalWeatherResponse] = None
        cache_entry = self.db.query(WeatherCache).filter(
            WeatherCache.location_key == cache_key,
            WeatherCache.expires_at > now
        ).first()

        if cache_entry:
            try:
                cached_dict = json.loads(cache_entry.cached_data)
                weather_data = AgriculturalWeatherResponse(**cached_dict)
            except Exception:
                weather_data = None

        if not weather_data:
            # Fetch fresh data from provider
            weather_data = self.provider.get_agricultural_weather(lat, lon, loc_name)

            # Update cache (1 hour TTL)
            try:
                expires = now + timedelta(hours=1)
                if cache_entry:
                    cache_entry.cached_data = weather_data.model_dump_json()
                    cache_entry.expires_at = expires
                else:
                    new_cache = WeatherCache(
                        location_key=cache_key,
                        cached_data=weather_data.model_dump_json(),
                        expires_at=expires
                    )
                    self.db.add(new_cache)
                self.db.commit()
            except Exception:
                self.db.rollback()

        # Localize presentation fields
        if clean_lang == "en":
            weather_data.advisory = weather_data.irrigation_advisory_en
        elif clean_lang == "hi":
            weather_data.advisory = weather_data.irrigation_advisory_hi
        else:
            weather_data.advisory = weather_data.irrigation_advisory_mr
        weather_data.language = clean_lang

        return weather_data
