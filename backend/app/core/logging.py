"""Structured (JSON) logging with request-correlation support.

In development, plain human-readable lines are easier to scan in a
terminal. In staging/production, every log line is JSON — the shape every
log aggregator (CloudWatch, Datadog, Loki, ELK) expects, and each line
automatically carries the current request's correlation ID (see
app.core.middleware.RequestIDMiddleware) via a contextvar, so a single
request's logs can be grepped/filtered across every layer that logs
(endpoint, service, repository) without threading a request object through
every function signature.
"""

import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any

from app.core.config import settings

_request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


def set_request_id(request_id: str | None) -> None:
    _request_id_ctx.set(request_id)


def get_request_id() -> str | None:
    return _request_id_ctx.get()


class RequestIDFilter(logging.Filter):
    """Attaches the current request's correlation ID (if any) to every
    LogRecord, so both the JSON and human-readable formatters can include
    it without every call site passing it explicitly."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        request_id = getattr(record, "request_id", None)
        if request_id:
            payload["request_id"] = request_id
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        # Allow call sites to pass structured extras via `extra={...}`
        # without them being swallowed — anything not already a standard
        # LogRecord attribute is merged in verbatim.
        standard_keys = logging.LogRecord(
            "", 0, "", 0, "", (), None
        ).__dict__.keys()
        for key, value in record.__dict__.items():
            if key not in standard_keys and key not in payload and key != "request_id":
                payload[key] = value
        return json.dumps(payload, default=str)


def configure_logging() -> None:
    """Configure application-wide logging. JSON in production/staging,
    human-readable in development/test — controlled by settings.is_production
    plus a simple staging check, not a separate flag, so there's one fewer
    setting to misconfigure."""
    use_json = settings.ENVIRONMENT.value in ("production", "staging")

    if use_json:
        formatter: logging.Formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(RequestIDFilter())

    root = logging.getLogger()
    root.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    root.handlers = [handler]

    # Quiet noisy third-party loggers; access logging is handled by our own
    # RequestLoggingMiddleware instead, which includes timing and status.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
