import json
import logging
import sys
import time
import uuid
from contextvars import ContextVar
from functools import wraps
from typing import Any, Dict, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

try:
    from pythonjsonlogger import jsonlogger
    HAS_JSON_LOGGER = True
except ImportError:
    HAS_JSON_LOGGER = False

correlation_id_var: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)


class JSONFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if HAS_JSON_LOGGER:
            self._json_formatter = jsonlogger.JsonFormatter(
                '%(timestamp)s %(level)s %(name)s %(message)s',
                timestamp='%Y-%m-%dT%H:%M:%S.%fZ',
            )
        else:
            self._json_formatter = None

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            'timestamp': self.formatTime(record, '%Y-%m-%dT%H:%M:%S.%fZ'),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }

        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        correlation_id = correlation_id_var.get()
        if correlation_id:
            log_data['correlation_id'] = correlation_id

        user_id = user_id_var.get()
        if user_id:
            log_data['user_id'] = user_id

        for key, value in record.__dict__.items():
            if key not in {
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                'filename', 'module', 'lineno', 'funcName', 'created',
                'msecs', 'relativeCreated', 'thread', 'threadName',
                'processName', 'process', 'exc_info', 'exc_text', 'stack_info',
                'message',
            }:
                log_data[key] = value

        if self._json_formatter:
            return self._json_formatter.format(logging.LogRecord(
                name=record.name,
                level=record.levelno,
                pathname=record.pathname,
                lineno=record.lineno,
                msg=json.dumps(log_data),
                args=(),
                exc_info=record.exc_info,
            ))
        return json.dumps(log_data, default=str)


def configure_logging(settings) -> None:
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    if settings.ENVIRONMENT == 'production':
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                datefmt='%Y-%m-%dT%H:%M:%S',
            )
        )

    root_logger.addHandler(console_handler)

    logging.getLogger('uvicorn.access').handlers = []
    logging.getLogger('uvicorn.error').handlers = []
    logging.getLogger('uvicorn').propagate = True


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()

        correlation_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
        correlation_id_var.set(correlation_id)

        user_id = None
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            try:
                from app.core.security import decode_access_token
                token = auth_header[7:]
                payload = decode_access_token(token)
                user_id = payload.get('sub')
                if user_id:
                    user_id_var.set(user_id)
            except Exception:
                pass

        client_ip = request.client.host if request.client else 'unknown'
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            client_ip = forwarded_for.split(',')[0].strip()

        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000

            logger = logging.getLogger('dav.request')
            logger.info(
                'HTTP request completed',
                extra={
                    'method': request.method,
                    'path': request.url.path,
                    'status_code': response.status_code,
                    'duration_ms': round(duration_ms, 2),
                    'user_id': user_id,
                    'client_ip': client_ip,
                    'correlation_id': correlation_id,
                },
            )

            response.headers['X-Request-ID'] = correlation_id
            return response

        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000

            logger = logging.getLogger('dav.request')
            logger.error(
                'HTTP request failed',
                extra={
                    'method': request.method,
                    'path': request.url.path,
                    'duration_ms': round(duration_ms, 2),
                    'user_id': user_id,
                    'client_ip': client_ip,
                    'correlation_id': correlation_id,
                    'error': str(exc),
                },
                exc_info=True,
            )
            raise


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def audit_log(action: str, user_id: Optional[str], details: Dict[str, Any]) -> None:
    logger = logging.getLogger('dav.audit')
    logger.info(
        'Audit log entry',
        extra={
            'audit': True,
            'action': action,
            'user_id': user_id,
            'details': details,
        },
    )


def audit_log_decorator(action: str, user_id_getter):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user_id = user_id_getter(*args, **kwargs) if user_id_getter else None
            try:
                result = await func(*args, **kwargs)
                audit_log(action, user_id, {'status': 'success'})
                return result
            except Exception as exc:
                audit_log(action, user_id, {'status': 'failure', 'error': str(exc)})
                raise
        return wrapper
    return decorator
