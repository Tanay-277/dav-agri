from app.integrations.weather.base import BaseWeatherProvider
from app.schemas.weather import AgriculturalWeatherResponse, TimeSlotForecast

class MockWeatherProvider(BaseWeatherProvider):
    def get_agricultural_weather(
        self,
        lat: float,
        lon: float,
        location_name: str = "Pune, MH"
    ) -> AgriculturalWeatherResponse:
        return AgriculturalWeatherResponse(
            location=location_name,
            temperature_c=27.0,
            condition="Rain",
            expected_rainfall_mm=40.0,
            duration_hours=3,
            intensity="heavy",
            intensity_level=3,
            irrigation_needed=False,
            irrigation_advisory_en="No irrigation needed today due to expected 40mm rain.",
            irrigation_advisory_hi="आज सिंचाई की ज़रूरत नहीं है",
            irrigation_advisory_mr="आज शेतात पाणी देण्याची गरज नाही, 40mm पाऊस अपेक्षित आहे.",
            is_live=False,
            source="mock",
            time_slots=[
                TimeSlotForecast(period="morning", label_en="Morning", label_hi="सुबह", label_mr="सकाळ", temp_c=24.0, condition="sunny_cloud", rain_probability=20),
                TimeSlotForecast(period="afternoon", label_en="Afternoon", label_hi="दोपहर", label_mr="दुपार", temp_c=27.0, condition="rain", rain_probability=85),
                TimeSlotForecast(period="evening", label_en="Evening", label_hi="शाम", label_mr="संध्याकाळ", temp_c=25.0, condition="rain_sun", rain_probability=70),
                TimeSlotForecast(period="night", label_en="Night", label_hi="रात", label_mr="रात्र", temp_c=22.0, condition="cloud", rain_probability=30),
            ]
        )
