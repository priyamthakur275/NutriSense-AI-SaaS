"""Blanket audit-trail middleware — the deliberate architectural choice for
Phase 6's "Track: CRUD operations... Permission changes... Security
events" requirement. Rather than threading an audit-log call through every
one of the ~50 endpoint functions across the API (which would mean
touching a large amount of already-completed, already-verified Phase 4D/5
code), this middleware observes every request generically:

  - Any mutating request (POST/PUT/PATCH/DELETE) that succeeds is logged
    as CREATE/UPDATE/DELETE, with entity_type/entity_id inferred from the
    URL path.
  - Any request that comes back 401/403 is logged as ACCESS_DENIED — this
    automatically covers every RBAC permission check (app.api.rbac) and
    every tenant-isolation check (app.api.tenant_scope) with zero
    additional code in either module, since both simply raise an
    HTTPException/AppError that surfaces as one of those status codes.

Login/logout/register are deliberately excluded here — app.services.
auth_service already writes more specific, richer audit entries for those
(LOGIN, LOGOUT, LOGIN_FAILED) with context this generic middleware doesn't
have (e.g. distinguishing a wrong password from a locked account). Double-
logging them generically here would just add noise.

Audit logging failures must never break the actual request — write
failures here are caught and logged as a warning, not propagated.
"""

import re

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger
from app.core.security import TokenType, decode_token

logger = get_logger("app.audit")

_MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

_METHOD_TO_ACTION = {
    "POST": "create",
    "PUT": "update",
    "PATCH": "update",
    "DELETE": "delete",
}

# Paths this middleware should never generically audit-log — either because
# a more specific/richer log entry is already written elsewhere (auth), or
# because they're not application data mutations at all (docs/metrics).
_EXCLUDED_PATH_PREFIXES = (
    "/api/v1/auth/",
    "/api/v1/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/metrics",
)

# Matches "/api/v1/<resource>" or "/api/v1/<resource>/<id>[/...]" and
# extracts both — used to fill AuditLog.entity_type / entity_id without
# each endpoint needing to declare it explicitly.
_PATH_PATTERN = re.compile(r"^/api/v1/([a-zA-Z0-9\-]+)(?:/([a-zA-Z0-9\-]+))?")


def _extract_user_id(request: Request) -> str | None:
    """Best-effort extraction of the caller's user id from the JWT, without
    a DB round-trip — this middleware only needs the `sub` claim, not the
    full validated User object app.api.deps.get_current_user resolves for
    the actual request handling."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header.removeprefix("Bearer ").strip()
    payload = decode_token(token, expected_type=TokenType.ACCESS)
    if not payload:
        return None
    return payload.get("sub")


def _entity_info(path: str) -> tuple[str | None, str | None]:
    match = _PATH_PATTERN.match(path)
    if not match:
        return None, None
    return match.group(1), match.group(2)


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)

        path = request.url.path
        if any(path.startswith(prefix) for prefix in _EXCLUDED_PATH_PREFIXES):
            return response

        should_log_mutation = request.method in _MUTATING_METHODS and response.status_code < 400
        should_log_denial = response.status_code in (401, 403)

        if not should_log_mutation and not should_log_denial:
            return response

        try:
            self._write_audit_entry(request, response, should_log_denial)
        except Exception:
            logger.exception("Audit logging failed (request was not affected)")

        return response

    def _write_audit_entry(self, request: Request, response: Response, is_denial: bool) -> None:
        from app.db.session import SessionLocal
        from app.models.audit_log import AuditLog
        from app.models.enums import AuditAction

        user_id = _extract_user_id(request)
        entity_type, entity_id = _entity_info(request.url.path)
        client_ip = request.client.host if request.client else None

        if is_denial:
            action = AuditAction.ACCESS_DENIED
        else:
            action = AuditAction(_METHOD_TO_ACTION[request.method])

        db = SessionLocal()
        try:
            db.add(
                AuditLog(
                    user_id=user_id,
                    action=action,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    ip_address=client_ip,
                    details={
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": response.status_code,
                    },
                )
            )
            db.commit()
        finally:
            db.close()
