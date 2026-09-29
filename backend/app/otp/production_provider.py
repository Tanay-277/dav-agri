import secrets
import logging
import httpx
from app.core.config import settings
from app.otp.base import BaseOTPProvider

logger = logging.getLogger(__name__)

class ProductionOTPProvider(BaseOTPProvider):
    """Production OTP Provider that delivers SMS via Twilio REST API."""

    def __init__(
        self,
        account_sid: str = "",
        auth_token: str = "",
        from_number: str = ""
    ):
        self.account_sid = account_sid or settings.TWILIO_ACCOUNT_SID
        self.auth_token = auth_token or settings.TWILIO_AUTH_TOKEN
        self.from_number = from_number or settings.TWILIO_FROM_NUMBER

    @property
    def provider_name(self) -> str:
        return "twilio"

    @property
    def is_production(self) -> bool:
        return True

    def generate_otp(self) -> str:
        """Generate cryptographically secure 5-digit OTP (10000 - 99999)."""
        return str(secrets.randbelow(90000) + 10000)

    def send_otp(self, phone: str, otp: str) -> bool:
        if not self.account_sid or not self.auth_token or not self.from_number:
            logger.error("[TWILIO OTP] Missing Twilio credentials (ACCOUNT_SID, AUTH_TOKEN, or FROM_NUMBER)")
            raise RuntimeError("Twilio SMS credentials are not properly configured")

        # Format Indian phone number if missing country prefix
        recipient = phone.strip()
        if not recipient.startswith("+"):
            if len(recipient) == 10:
                recipient = f"+91{recipient}"
            else:
                recipient = f"+{recipient}"

        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
        masked_phone = recipient[:4] + "***" + recipient[-3:] if len(recipient) > 7 else "***"
        
        try:
            with httpx.Client(timeout=8.0) as client:
                response = client.post(
                    url,
                    auth=(self.account_sid, self.auth_token),
                    data={
                        "From": self.from_number,
                        "To": recipient,
                        "Body": f"Your DAV verification code is {otp}. Valid for 5 minutes."
                    }
                )

                if response.status_code in (200, 201):
                    logger.info(f"[TWILIO OTP] Successfully dispatched SMS to {masked_phone}")
                    return True
                else:
                    logger.error(
                        f"[TWILIO OTP] Delivery failed to {masked_phone}. Status: {response.status_code}, Body: {response.text}"
                    )
                    return False
        except httpx.HTTPError as e:
            logger.error(f"[TWILIO OTP] Network exception delivering SMS to {masked_phone}: {e}")
            return False
