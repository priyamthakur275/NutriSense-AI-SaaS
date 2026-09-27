"""Combines two concerns that both need to wrap the full request/response
cycle, so they're one middleware rather than two competing for ordering:

1. Request ID / correlation ID — read from the incoming `X-Request-ID`
   header if the caller (e.g. an API gateway) already assigned one,
   otherwise generated fresh. Stored in a contextvar so every log line
   emitted while handling this request can include it (see
   app.core.logging), and echoed back in the response header so a client
   can correlate their request with server-side logs when reporting a bug.

2. Request logging — one structured log line per request, with method,
   path, status code, and duration. This replaces uvicorn's default access
   log (silenced in app.core.logging.configure_logging) so timing and the
   request ID are always present together.
"""

import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings
from app.core.logging import get_logger, set_request_id
from app.core.metrics import record_request

logger = get_logger("app.request")

REQUEST_ID_HEADER = "X-Request-ID"


def _route_template(request: Request) -> str:
    """Returns the matched route's path template (e.g.
    '/api/v1/meals/{meal_id}') rather than the raw URL path — using the raw
    path as a metric label would create a new time series per unique UUID
    ever requested, an unbounded-cardinality footgun. Falls back to the raw
    path only for genuinely unmatched routes (404s), which is an acceptable,
    bounded exception."""
    route = request.scope.get("route")
    if route is not None and hasattr(route, "path"):
        return route.path
    return request.url.path


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())
        set_request_id(request_id)
        request.state.request_id = request_id

        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.exception(
                "Unhandled exception during request",
                extra={
                    "http_method": request.method,
                    "http_path": request.url.path,
                    "duration_ms": duration_ms,
                },
            )
            raise
        finally:
            set_request_id(None)

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers[REQUEST_ID_HEADER] = request_id
        route_path = _route_template(request)

        if settings.METRICS_ENABLED:
            record_request(
                method=request.method,
                path=route_path,
                status_code=response.status_code,
                duration_seconds=duration_ms / 1000,
            )

        log_level = logger.warning if response.status_code >= 400 else logger.info
        log_level(
            "%s %s -> %d (%.2fms)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            extra={
                "http_method": request.method,
                "http_path": request.url.path,
                "http_status": response.status_code,
                "duration_ms": duration_ms,
                "client_ip": request.client.host if request.client else None,
            },
        )
        return response
