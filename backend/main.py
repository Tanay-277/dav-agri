from __future__ import annotations

import time
from collections import defaultdict
from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from api.routes import router
from api.voice_api import router as voice_router
from core.config import get_settings
from core.logging import configure_logging, get_logger
from core.middleware import RequestLoggingMiddleware
from database.db import init_db
from speech_to_text.api import router as speech_router
from text_to_speech.api import router as tts_router

configure_logging()
logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiter: 100 requests / 60 seconds per IP."""

    def __init__(self, app: FastAPI, max_requests: int = 100, window: int = 60) -> None:
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self._store: Dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        timestamps = self._store[client_ip]
        timestamps[:] = [t for t in timestamps if now - t < self.window]
        if len(timestamps) >= self.max_requests:
            logger.warning("Rate limit exceeded for %s", client_ip)
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please try again later."},
            )
        timestamps.append(now)
        return await call_next(request)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("Startup complete")
    yield


settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description=(
        "Backend for the Interactive Data Storytelling Dashboard for "
        "Agricultural Analytics."
    ),
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RateLimitMiddleware, max_requests=100, window=60)
app.add_middleware(RequestLoggingMiddleware)

app.include_router(router, prefix="/api/v1")
app.include_router(voice_router, prefix="/api/v1/voice")
app.include_router(speech_router, prefix="/api/v1/speech")
app.include_router(tts_router, prefix="/api/v1/tts")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled exception on %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please contact support."},
    )


@app.get("/")
def root() -> dict:
    return {
        "app": settings.APP_NAME,
        "docs": "/docs",
        "health": "/api/health",
    }
