import logging
from app.core.config import settings
from app.otp.base import BaseOTPProvider

logger = logging.getLogger(__name__)

class MockOTPProvider(BaseOTPProvider):
    @property
    def provider_name(self) -> str:
        return "mock"

    @property
    def is_production(self) -> bool:
        return False

    def generate_otp(self) -> str:
        # Dev mock OTP defaults to "44444" matching Figma Screen 4
        return settings.DEV_MOCK_OTP or "44444"

    def send_otp(self, phone: str, otp: str) -> bool:
        logger.info(f"[DEV MOCK OTP] Simulated SMS to {phone}: Verification code is '{otp}' (valid 5 mins)")
        return True
