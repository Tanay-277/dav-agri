from app.schemas.common import APIResponse, ErrorDetail
from app.schemas.auth import (
    RequestOtpRequest,
    RequestOtpResponse,
    VerifyOtpRequest,
    GoogleAuthRequest,
    TokenResponse,
    CurrentUserResponse,
)
from app.schemas.profile import ProfileBase, ProfileUpdate, ProfileRead
from app.schemas.onboarding import (
    OnboardingStatusResponse,
    ConfirmLanguageRequest,
    UpdateOnboardingRequest,
)
from app.schemas.farm import (
    CropRead,
    ProductionRecordCreate,
    ProductionRecordRead,
    ExpenseRecordCreate,
    ExpenseRecordRead,
    ExpenseBreakdownResponse,
    StructuredVisualization,
    FarmSummaryResponse,
)
from app.schemas.weather import (
    TimeSlotForecast,
    AgriculturalWeatherResponse,
)
from app.schemas.query import (
    QueryRequest,
    QueryResponse,
    ConversationItem,
)
from app.schemas.voice import (
    TranscribeResponse,
    SynthesizeRequest,
    VoiceSampleResponse,
)

__all__ = [
    "APIResponse",
    "ErrorDetail",
    "RequestOtpRequest",
    "RequestOtpResponse",
    "VerifyOtpRequest",
    "GoogleAuthRequest",
    "TokenResponse",
    "CurrentUserResponse",
    "ProfileBase",
    "ProfileUpdate",
    "ProfileRead",
    "OnboardingStatusResponse",
    "ConfirmLanguageRequest",
    "UpdateOnboardingRequest",
    "CropRead",
    "ProductionRecordCreate",
    "ProductionRecordRead",
    "ExpenseRecordCreate",
    "ExpenseRecordRead",
    "ExpenseBreakdownResponse",
    "StructuredVisualization",
    "FarmSummaryResponse",
    "TimeSlotForecast",
    "AgriculturalWeatherResponse",
    "QueryRequest",
    "QueryResponse",
    "ConversationItem",
    "TranscribeResponse",
    "SynthesizeRequest",
    "VoiceSampleResponse",
]
