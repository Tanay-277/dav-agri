from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    APP_SECRET_KEY: str = "dav_dev_secret_key_99881122"
    API_V1_STR: str = "/api/v1"

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    # Database
    DATABASE_URL: str = "sqlite:///./dav.db"

    # JWT
    JWT_SECRET: str = "dav_dev_jwt_secret_99881122_very_secure_key_for_development_32bytes"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    # OTP
    DEV_MOCK_OTP: str = "44444"
    OTP_PROVIDER: str = "mock"  # "mock", "twilio"
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_FROM_NUMBER: str = ""

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # AI Configuration
    AI_PROVIDER: str = "mock"  # "gemini", "openai", "mock"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    OPENAI_API_KEY: str = ""

    # Voice Configuration
    VOICE_STT_PROVIDER: str = "mock"  # "google", "whisper", "local", "mock"
    VOICE_TTS_PROVIDER: str = "mock"  # "google", "edge_tts", "local", "mock"
    VOICE_API_KEY: str = ""

    # Weather Configuration
    WEATHER_PROVIDER: str = "openmeteo"  # "openmeteo", "openweathermap", "mock"
    OPENWEATHER_API_KEY: str = ""
    DEFAULT_LATITUDE: float = 18.5204
    DEFAULT_LONGITUDE: float = 73.8567
    DEFAULT_LOCATION_NAME: str = "Pune, MH"

settings = Settings()

def log_startup_configuration():
    """Logs the backend service status on startup without exposing secrets.
    Enforces production security guards in production mode."""
    import logging
    logger = logging.getLogger("dav.config")

    if settings.ENVIRONMENT.lower() == "production":
        # Production security guards
        if "dev_secret" in settings.APP_SECRET_KEY or settings.APP_SECRET_KEY == "dav_dev_secret_key_99881122":
            raise RuntimeError("CRITICAL SECURITY ERROR: APP_SECRET_KEY must be set to a secure secret in production.")
        if "dev_jwt" in settings.JWT_SECRET or settings.JWT_SECRET.startswith("dav_dev_jwt_secret"):
            raise RuntimeError("CRITICAL SECURITY ERROR: JWT_SECRET must be set to a secure secret in production.")
        if settings.OTP_PROVIDER == "twilio":
            if not (settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_FROM_NUMBER):
                raise RuntimeError("CRITICAL CONFIGURATION ERROR: Twilio OTP provider requires TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_FROM_NUMBER in production.")

    # Determine status representations
    ai_status = (
        f"Google Gemini ({settings.GEMINI_MODEL}) [Configured]"
        if settings.GEMINI_API_KEY
        else "MockAIProvider (Fallback - GEMINI_API_KEY not set)"
    )

    if settings.OTP_PROVIDER == "twilio" and settings.TWILIO_ACCOUNT_SID:
        masked_sid = settings.TWILIO_ACCOUNT_SID[:6] + "..." + settings.TWILIO_ACCOUNT_SID[-4:] if len(settings.TWILIO_ACCOUNT_SID) > 10 else "***"
        otp_status = f"Twilio SMS (Production active, SID: {masked_sid})"
    else:
        otp_status = f"MockOTPProvider (Development active, accepts '{settings.DEV_MOCK_OTP}')"

    if settings.GOOGLE_CLIENT_ID:
        masked_gid = settings.GOOGLE_CLIENT_ID[:8] + "..." if len(settings.GOOGLE_CLIENT_ID) > 8 else "***"
        google_status = f"Google OAuth [Configured, Client ID: {masked_gid}]"
    else:
        google_status = "Development Mock (GOOGLE_CLIENT_ID not set)"

    logger.info("=" * 60)
    logger.info("DAV BACKEND CONFIGURATION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"  Environment:    {settings.ENVIRONMENT}")
    logger.info(f"  Debug Mode:     {settings.DEBUG}")
    logger.info(f"  Database URL:   {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
    logger.info(f"  AI Provider:    {ai_status}")
    logger.info(f"  OTP Provider:   {otp_status}")
    logger.info(f"  Google OAuth:   {google_status}")
    logger.info(f"  Weather Engine: Open-Meteo ({settings.WEATHER_PROVIDER})")
    logger.info(f"  Voice (TTS):    Microsoft Edge Neural TTS (with gTTS fallback)")
    logger.info("=" * 60)

