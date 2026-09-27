"""Standard security response headers. None of these are exotic — they're
the well-known baseline (OWASP Secure Headers Project) that costs nothing
to apply and closes off a class of browser-side attacks (clickjacking,
MIME-sniffing, referrer leakage) regardless of what any individual endpoint
does. Applied uniformly rather than per-route so nothing can accidentally
ship without them.
"""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings

_STATIC_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    # Relaxed CSP for the integrated React SPA.
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; font-src 'self' data:; frame-ancestors 'none'",
}

_DOCS_PATHS = {"/docs", "/redoc", "/openapi.json"}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)

        for header, value in _STATIC_HEADERS.items():
            if header == "Content-Security-Policy" and request.url.path in _DOCS_PATHS:
                continue
            response.headers.setdefault(header, value)

        if settings.is_production:
            response.headers.setdefault(
                "Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload"
            )

        return response
