from app.core.config import settings
from app.otp.base import BaseOTPProvider
from app.otp.mock_provider import MockOTPProvider
from app.otp.production_provider import ProductionOTPProvider

def get_otp_provider() -> BaseOTPProvider:
    """Factory to retrieve the configured OTP provider.
    Falls back cleanly to MockOTPProvider in development mode or if credentials are incomplete.
    """
    if settings.OTP_PROVIDER == "twilio" and settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
        return ProductionOTPProvider(
            account_sid=settings.TWILIO_ACCOUNT_SID,
            auth_token=settings.TWILIO_AUTH_TOKEN,
            from_number=settings.TWILIO_FROM_NUMBER
        )
    return MockOTPProvider()

__all__ = ["BaseOTPProvider", "MockOTPProvider", "ProductionOTPProvider", "get_otp_provider"]
