from app.core.config import settings
from app.integrations.weather.base import BaseWeatherProvider
from app.integrations.weather.mock_provider import MockWeatherProvider
from app.integrations.weather.openmeteo_provider import OpenMeteoWeatherProvider

def get_weather_provider() -> BaseWeatherProvider:
    if settings.WEATHER_PROVIDER == "openmeteo":
        return OpenMeteoWeatherProvider()
    return MockWeatherProvider()

__all__ = ["BaseWeatherProvider", "MockWeatherProvider", "OpenMeteoWeatherProvider", "get_weather_provider"]
