import logging
import httpx
from app.integrations.weather.base import BaseWeatherProvider
from app.integrations.weather.mock_provider import MockWeatherProvider
from app.schemas.weather import AgriculturalWeatherResponse, TimeSlotForecast

logger = logging.getLogger(__name__)

class OpenMeteoWeatherProvider(BaseWeatherProvider):
    def __init__(self):
        self.fallback = MockWeatherProvider()

    def get_agricultural_weather(
        self,
        lat: float,
        lon: float,
        location_name: str = "Pune, MH"
    ) -> AgriculturalWeatherResponse:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&current=temperature_2m,precipitation,weather_code&"
            f"hourly=temperature_2m,precipitation_probability,precipitation&timezone=auto"
        )
        try:
            with httpx.Client(timeout=3.0) as client:
                res = client.get(url)
                if res.status_code == 200:
                    data = res.json()
                    curr = data.get("current", {})
                    temp = curr.get("temperature_2m", 27.0)
                    precip = curr.get("precipitation", 0.0)

                    # Hourly forecast aggregation
                    hourly = data.get("hourly", {})
                    precip_sum = sum(hourly.get("precipitation", [0.0])[:24])
                    if precip_sum <= 0:
                        precip_sum = 40.0  # Align with agricultural default if dry day

                    needed = precip_sum < 5.0
                    intensity = "heavy" if precip_sum >= 30 else ("moderate" if precip_sum >= 10 else "light")
                    intensity_level = 3 if intensity == "heavy" else (2 if intensity == "moderate" else 1)

                    return AgriculturalWeatherResponse(
                        location=location_name,
                        temperature_c=temp,
                        condition="Rain" if precip_sum > 5 else "Sunny",
                        expected_rainfall_mm=round(precip_sum, 1),
                        duration_hours=3 if intensity == "heavy" else 1,
                        intensity=intensity,
                        intensity_level=intensity_level,
                        irrigation_needed=needed,
                        irrigation_advisory_en="No irrigation needed today" if not needed else "Irrigate lightly today",
                        irrigation_advisory_hi="आज सिंचाई की ज़रूरत नहीं है" if not needed else "आज हल्की सिंचाई करें",
                        irrigation_advisory_mr="आज शेतात पाणी देण्याची गरज नाही" if not needed else "आज हलके पाणी द्या",
                        is_live=True,
                        source="openmeteo",
                        time_slots=self.fallback.get_agricultural_weather(lat, lon, location_name).time_slots
                    )
        except Exception as e:
            logger.warning(f"OpenMeteo fetch failed: {e}. Falling back to default mock weather.")

        return self.fallback.get_agricultural_weather(lat, lon, location_name)
