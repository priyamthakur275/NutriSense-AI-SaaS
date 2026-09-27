"""Persistence and lifecycle management for the three DB-tracked token
types (RefreshToken, PasswordResetToken, EmailVerificationToken).

Kept separate from `auth_service` (which orchestrates the auth *flows*) so
token storage/lookup/revocation logic has a single owner — auth_service
calls into this, never touches these tables directly.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_refresh_token,
    generate_opaque_token,
    hash_opaque_token,
)
from app.models.email_verification_token import EmailVerificationToken
from app.models.password_reset_token import PasswordResetToken
from app.models.refresh_token import RefreshToken
from app.models.user import User


# ---------------------------------------------------------------------------
# Refresh tokens
# ---------------------------------------------------------------------------


def issue_refresh_token(
    db: Session, user: User, *, user_agent: str | None = None, ip_address: str | None = None
) -> str:
    """Creates a RefreshToken row and returns the raw JWT to hand to the
    client. The row's own UUID is used as the JWT's `jti` claim, so a
    presented token can be looked up by hashing it — no need to trust the
    claim alone."""
    raw_jwt, jti, expires_at = create_refresh_token(subject=user.id)

    token_row = RefreshToken(
        id=UUID(jti),
        user_id=user.id,
        token_hash=hash_opaque_token(raw_jwt),
        expires_at=expires_at,
        user_agent=user_agent,
        ip_address=ip_address,
    )
    db.add(token_row)
    db.flush()
    return raw_jwt


def get_active_refresh_token(db: Session, raw_token: str) -> RefreshToken | None:
    token_hash = hash_opaque_token(raw_token)
    row = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
    if row is None or not row.is_active:
        return None
    return row


def rotate_refresh_token(
    db: Session, old_token_row: RefreshToken, *, user_agent: str | None = None, ip_address: str | None = None
) -> str:
    """Issues a new refresh token and marks the old one revoked + linked to
    its replacement (rotation chain). Called only after the old token has
    already been validated as active by the caller."""
    new_raw_jwt = issue_refresh_token(
        db, old_token_row.user, user_agent=user_agent, ip_address=ip_address
    )
    new_row = get_active_refresh_token(db, new_raw_jwt)

    old_token_row.revoke()
    if new_row is not None:
        old_token_row.replaced_by_id = new_row.id
    db.flush()
    return new_raw_jwt


def revoke_refresh_token(db: Session, raw_token: str) -> bool:
    row = db.query(RefreshToken).filter(
        RefreshToken.token_hash == hash_opaque_token(raw_token)
    ).first()
    if row is None:
        return False
    row.revoke()
    db.flush()
    return True


def revoke_all_refresh_tokens_for_user(db: Session, user: User) -> None:
    """Called on password change/reset — invalidates every existing session
    so a stolen-but-not-yet-used token from before the change stops working."""
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user.id, RefreshToken.revoked_at.is_(None)
    ).update({"revoked_at": datetime.now(timezone.utc)})
    db.flush()


# ---------------------------------------------------------------------------
# Password reset tokens
# ---------------------------------------------------------------------------


def issue_password_reset_token(db: Session, user: User) -> str:
    raw_token = generate_opaque_token()
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
    )
    db.add(
        PasswordResetToken(
            user_id=user.id, token_hash=hash_opaque_token(raw_token), expires_at=expires_at
        )
    )
    db.flush()
    return raw_token


def consume_password_reset_token(db: Session, raw_token: str) -> PasswordResetToken | None:
    """Validates and marks the token used, atomically from the caller's
    perspective (caller must still commit). Returns None if invalid/expired/
    already used — the caller should treat that as a generic invalid-token
    error, never distinguishing "expired" from "already used" to a client."""
    row = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == hash_opaque_token(raw_token)
    ).first()
    if row is None or not row.is_valid:
        return None
    row.mark_used()
    db.flush()
    return row


# ---------------------------------------------------------------------------
# Email verification tokens
# ---------------------------------------------------------------------------


def issue_email_verification_token(db: Session, user: User) -> str:
    raw_token = generate_opaque_token()
    expires_at = datetime.now(timezone.utc) + timedelta(
        hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS
    )
    db.add(
        EmailVerificationToken(
            user_id=user.id, token_hash=hash_opaque_token(raw_token), expires_at=expires_at
        )
    )
    db.flush()
    return raw_token


def consume_email_verification_token(db: Session, raw_token: str) -> EmailVerificationToken | None:
    row = db.query(EmailVerificationToken).filter(
        EmailVerificationToken.token_hash == hash_opaque_token(raw_token)
    ).first()
    if row is None or not row.is_valid:
        return None
    row.mark_used()
    db.flush()
    return row
