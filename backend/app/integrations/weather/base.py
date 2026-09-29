from abc import ABC, abstractmethod
from typing import Dict, Any
from app.schemas.weather import AgriculturalWeatherResponse

class BaseWeatherProvider(ABC):
    @abstractmethod
    def get_agricultural_weather(
        self,
        lat: float,
        lon: float,
        location_name: str = "Pune, MH"
    ) -> AgriculturalWeatherResponse:
        """Fetch agricultural weather and irrigation recommendation."""
        pass
