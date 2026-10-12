import json
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.integrations.soil import get_soil_provider
from app.integrations.soil.mock_provider import MockSoilProvider
from app.models.query import SoilCache
from app.schemas.soil import SoilDataResponse

PROPERTY_LABELS = {
    "ph": {"en": "pH", "hi": "pH", "mr": "pH"},
    "organic_carbon_g_kg": {"en": "Organic Carbon", "hi": "कार्बनिक कार्बन", "mr": "कार्बनिक कार्बन"},
    "bulk_density_kg_m3": {"en": "Bulk Density", "hi": "घनत्व", "mr": "घनत्व"},
    "cec_mmolc_kg": {"en": "CEC", "hi": "CEC", "mr": "CEC"},
    "nitrogen_g_kg": {"en": "Nitrogen", "hi": "नाइट्रोजन", "mr": "नाइट्रोजन"},
    "sand_pct": {"en": "Sand", "hi": "बालू", "mr": "बालू"},
    "silt_pct": {"en": "Silt", "hi": "सिल्ट", "mr": "सिल्ट"},
    "clay_pct": {"en": "Clay", "hi": "चिकनी माटी", "mr": "चिकनी माटी"},
    "caco3_pct": {"en": "Calcium Carbonate", "hi": "कैल्शियम कार्बोनेट", "mr": "कैल्शियम कार्बोनेट"},
    "ocs_t_ha": {"en": "Organic Carbon Stock", "hi": "कार्बनिक कार्बन भंडार", "mr": "कार्बनिक कार्बन भंडार"},
    "wwp_pct": {"en": "Wilting Point", "hi": "viltiNga bindu", "mr": "viltiNga bindu"},
    "cfvo_pct": {"en": "Coarse Fragments", "hi": "स्थूल अंश", "mr": "स्थूल अंश"},
}


class SoilService:
    def __init__(self, db: Session):
        self.db = db
        self.provider = get_soil_provider()
        self.fallback = MockSoilProvider()

    def get_soil_data(
        self,
        lat: float = None,
        lon: float = None,
        location_name: str = None,
        language: str = "mr"
    ) -> SoilDataResponse:
        clean_lang = language.lower().strip()
        if clean_lang not in ("en", "hi", "mr"):
            raise ValueError(f"Unsupported language code {language}. Must be one of en, hi, mr")

        lang = clean_lang
        lat = lat if lat is not None else settings.DEFAULT_LATITUDE
        lon = lon if lon is not None else settings.DEFAULT_LONGITUDE
        loc_name = location_name or settings.DEFAULT_LOCATION_NAME

        cache_key = f"{round(lat, 2)}_{round(lon, 2)}"
        now = datetime.now(timezone.utc)

        cache_entry = self.db.query(SoilCache).filter(
            SoilCache.location_key == cache_key,
            SoilCache.expires_at > now
        ).first()

        soil_data = None

        if cache_entry:
            try:
                cached_dict = json.loads(cache_entry.cached_data)
                soil_data = SoilDataResponse(**cached_dict)
            except Exception:
                soil_data = None

        if soil_data is None:
            raw = None
            try:
                raw = self.provider.get_soil_data(lat=lat, lon=lon)
            except Exception:
                raw = None
            if raw is None:
                raw = self.fallback.get_soil_data(lat=lat, lon=lon)

            properties = raw.get("properties", {})
            localized_names = {
                key: PROPERTY_LABELS.get(key, {"en": key, "hi": key, "mr": key})
                for key in properties.keys()
            }
            soil_data = SoilDataResponse(
                location=raw.get("location", loc_name),
                properties=properties,
                source=raw.get("source", "soilgrids"),
                is_live=raw.get("is_live", True),
                language=lang,
                localized_names=localized_names,
            )

            expires_at = now + timedelta(hours=24)
            try:
                payload = soil_data.model_dump()
                cache_row = SoilCache(
                    location_key=cache_key,
                    cached_data=json.dumps(payload),
                    expires_at=expires_at,
                )
                self.db.merge(cache_row)
                self.db.commit()
            except Exception:
                self.db.rollback()

        return soil_data
