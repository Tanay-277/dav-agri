from abc import ABC, abstractmethod

class BaseOTPProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the OTP provider (e.g., 'mock', 'twilio')."""
        pass

    @property
    @abstractmethod
    def is_production(self) -> bool:
        """Whether this provider sends real production SMS."""
        pass

    @abstractmethod
    def generate_otp(self) -> str:
        """Generate an OTP string according to provider rules."""
        pass

    @abstractmethod
    def send_otp(self, phone: str, otp: str) -> bool:
        """Dispatch OTP to the designated phone number."""
        pass
