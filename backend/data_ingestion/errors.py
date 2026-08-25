from __future__ import annotations

from typing import Any


class DataIngestionError(Exception):
    """Base exception for data ingestion failures."""


class ProviderNotFoundError(DataIngestionError):
    """Raised when the configured provider is not registered."""


class APIError(DataIngestionError):
    """Raised when an external API returns an error response."""

    def __init__(
        self, message: str, status_code: int | None = None, body: Any = None
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class RateLimitError(APIError):
    """Raised when an external API returns a rate-limit response."""

    def __init__(
        self, message: str = "Rate limit exceeded", retry_after: int | None = None
    ) -> None:
        super().__init__(message, status_code=429)
        self.retry_after = retry_after


class ValidationError(DataIngestionError):
    """Raised when normalized data fails validation."""


class NetworkError(DataIngestionError):
    """Raised when a network-level failure occurs (timeout, DNS, connection refused)."""
