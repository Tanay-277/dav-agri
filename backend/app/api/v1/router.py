from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    onboarding,
    profile,
    farm,
    weather,
    query,
    voice,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(onboarding.router)
api_router.include_router(profile.router)
api_router.include_router(farm.router)
api_router.include_router(weather.router)
api_router.include_router(query.router)
api_router.include_router(voice.router)
