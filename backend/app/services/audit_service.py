"""Shared audit-log write helper.

Most mutations are already covered automatically by AuditMiddleware
(app.core.middleware.audit_middleware) — this function is for the minority
of cases that want a *richer* entry than the generic one the middleware
infers from the HTTP method/path alone (auth_service's LOGIN/LOGOUT/
LOGIN_FAILED entries, and now invite_service's entries), where the extra
context (why a login failed, that a user was created via an invite) is
worth capturing explicitly.
"""

from typing import Any

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.enums import AuditAction


def log_audit_event(
    db: Session,
    *,
    user_id: str | None,
    action: AuditAction,
    entity_type: str | None = None,
    entity_id: str | None = None,
    ip_address: str | None = None,
    details: dict[str, Any] | None = None,
) -> None:
    """Adds the AuditLog row to the session — does NOT commit; the caller's
    existing transaction (typically committing the entity change itself)
    covers it, so this never needs a separate round-trip."""
    db.add(
        AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            ip_address=ip_address,
            details=details,
        )
    )
