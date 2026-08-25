from __future__ import annotations

import logging
import time
import uuid
from typing import Awaitable, Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger("agristory.request")


def _generate_request_id() -> str:
    return uuid.uuid4().hex[:8]


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Structured request logging middleware."""

    def __init__(self, app, skip_paths: list[str] | None = None) -> None:
        super().__init__(app)
        self.skip_paths = set(skip_paths or ["/api/health", "/favicon.ico"])

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if request.url.path in self.skip_paths:
            return await call_next(request)

        request_id = _generate_request_id()
        start = time.perf_counter()

        log_extra = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query": dict(request.query_params),
            "client_ip": request.client.host if request.client else "unknown",
        }

        logger.info("request_start", extra=log_extra)

        try:
            response = await call_next(request)
        except Exception as exc:
            duration_ms = int((time.perf_counter() - start) * 1000)
            logger.error(
                "request_error",
                extra={
                    **log_extra,
                    "status": 500,
                    "duration_ms": duration_ms,
                    "error": str(exc),
                },
            )
            raise

        duration_ms = int((time.perf_counter() - start) * 1000)
        logger.info(
            "request_complete",
            extra={
                **log_extra,
                "status": response.status_code,
                "duration_ms": duration_ms,
            },
        )

        response.headers["X-Request-ID"] = request_id
        return response
