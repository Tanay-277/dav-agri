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
        hourly_vars = [
            "temperature_2m", "relative_humidity_2m", "precipitation", "precipitation_probability", "weather_code",
            "soil_temperature_0cm", "soil_temperature_6cm", "soil_temperature_18cm", "soil_temperature_54cm",
            "soil_moisture_0_to_1cm", "soil_moisture_1_to_3cm", "soil_moisture_3_to_9cm", "soil_moisture_9_to_27cm", "soil_moisture_27_to_81cm",
            "et0_fao_evapotranspiration",
            "shortwave_radiation", "vapour_pressure_deficit", "wind_speed_10m"
        ]
        daily_vars = [
            "temperature_2m_max", "temperature_2m_min", "precipitation_sum",
            "et0_fao_evapotranspiration", "sunshine_duration"
        ]
        current_vars = [
            "temperature_2m", "relative_humidity_2m", "precipitation", "precipitation_probability", "weather_code",
            "soil_temperature_0cm", "soil_temperature_6cm", "soil_temperature_18cm", "soil_temperature_54cm",
            "soil_moisture_0_to_1cm", "soil_moisture_1_to_3cm", "soil_moisture_3_to_9cm", "soil_moisture_9_to_27cm", "soil_moisture_27_to_81cm",
            "et0_fao_evapotranspiration",
            "shortwave_radiation", "vapour_pressure_deficit", "wind_speed_10m"
        ]
        url = "https://api.open-meteo.com/v1/forecast?" + "&".join([
            f"latitude={lat}",
            f"longitude={lon}",
            f"current={','.join(current_vars)}",
            f"hourly={','.join(hourly_vars)}",
            f"daily={','.join(daily_vars)}",
            "timezone=auto"
        ])
        try:
            with httpx.Client(timeout=5.0) as client:
                res = client.get(url)
                if res.status_code == 200:
                    data = res.json()
                    curr = data.get("current", {})
                    hourly = data.get("hourly", {})
                    daily = data.get("daily", {})

                    temp = curr.get("temperature_2m", 27.0)
                    precip = curr.get("precipitation", 0.0)
                    rel_humidity = curr.get("relative_humidity_2m")
                    precip_prob = curr.get("precipitation_probability")
                    weather_code = curr.get("weather_code")
                    wind_speed = curr.get("wind_speed_10m")
                    shortwave_rad = curr.get("shortwave_radiation")
                    vpd = curr.get("vapour_pressure_deficit")

                    soil_moisture_profile = {}
                    soil_temp_profile = {}
                    depth_map = {
                        "soil_moisture_0_to_1cm": "0-1cm",
                        "soil_moisture_1_to_3cm": "1-3cm",
                        "soil_moisture_3_to_9cm": "3-9cm",
                        "soil_moisture_9_to_27cm": "9-27cm",
                        "soil_moisture_27_to_81cm": "27-81cm",
                    }
                    temp_map = {
                        "soil_temperature_0cm": "0cm",
                        "soil_temperature_6cm": "6cm",
                        "soil_temperature_18cm": "18cm",
                        "soil_temperature_54cm": "54cm",
                    }
                    for key, label in depth_map.items():
                        if curr.get(key) is not None:
                            soil_moisture_profile[label] = curr[key]
                    for key, label in temp_map.items():
                        if curr.get(key) is not None:
                            soil_temp_profile[label] = curr[key]

                    et0_daily_mm = None
                    if daily.get("et0_fao_evapotranspiration"):
                        et0_daily_mm = round(daily["et0_fao_evapotranspiration"][0], 2)

                    precip_sum = sum(hourly.get("precipitation", [0.0])[:24])
                    if precip_sum <= 0:
                        precip_sum = 40.0

                    needed = precip_sum < 5.0
                    intensity = "heavy" if precip_sum >= 30 else ("moderate" if precip_sum >= 10 else "light")
                    intensity_level = 3 if intensity == "heavy" else (2 if intensity == "moderate" else 1)
                    condition = "Rain" if precip_sum > 5 else "Sunny"

                    return AgriculturalWeatherResponse(
                        location=location_name,
                        temperature_c=temp,
                        condition=condition,
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
                        time_slots=self.fallback.get_agricultural_weather(lat, lon, location_name).time_slots,
                        soil_moisture_profile=soil_moisture_profile if soil_moisture_profile else None,
                        soil_temperature_profile=soil_temp_profile if soil_temp_profile else None,
                        et0_mm=et0_daily_mm,
                        vpd_kpa=round(vpd, 2) if vpd is not None else None,
                        solar_radiation_w_m2=round(shortwave_rad, 1) if shortwave_rad is not None else None,
                        relative_humidity=rel_humidity,
                        precipitation_probability=precip_prob,
                        weather_code=weather_code,
                        wind_speed_ms=wind_speed,
                    )
        except Exception as e:
            logger.warning(f"OpenMeteo fetch failed: {e}. Falling back to default mock weather.")

        return self.fallback.get_agricultural_weather(lat, lon, location_name)