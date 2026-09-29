from typing import Generic, TypeVar, Optional, Any, Dict
from pydantic import BaseModel

T = TypeVar("T")

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

class APIResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[ErrorDetail] = None

    @classmethod
    def ok(cls, data: T) -> "APIResponse[T]":
        return cls(success=True, data=data, error=None)

    @classmethod
    def fail(cls, code: str, message: str, details: Optional[Dict[str, Any]] = None) -> "APIResponse[T]":
        return cls(success=False, data=None, error=ErrorDetail(code=code, message=message, details=details))
