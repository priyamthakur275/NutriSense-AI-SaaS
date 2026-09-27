"""Authentication orchestration: registration, login (with lockout),
token refresh/rotation, logout, and the password-reset / email-verification
flows. This is the single place business rules about "what counts as
authenticated" live — endpoints stay thin, calling into here.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import (
    AccountInactiveError,
    AccountLockedError,
    DuplicateResourceError,
    InvalidCredentialsError,
    InvalidTokenError,
)
from app.core.security import create_access_token, hash_password, needs_rehash, verify_password
from app.models.audit_log import AuditLog
from app.models.enums import AuditAction
from app.models.user import User
from app.schemas.user import UserCreate
from app.services import token_service
from app.services.email_service import (
    EmailService,
    build_password_reset_email,
    build_verification_email,
)
from app.utils.datetime_utils import ensure_aware


class DuplicateUserError(DuplicateResourceError):
    """Raised when attempting to register an email that already exists."""

    error_code = "duplicate_email"


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email, User.deleted_at.is_(None)).first()


def _log_audit(
    db: Session,
    *,
    user_id: str | None,
    action: AuditAction,
    ip_address: str | None = None,
    details: dict | None = None,
) -> None:
    db.add(AuditLog(user_id=user_id, action=action, ip_address=ip_address, details=details))


def _issue_token_pair(
    db: Session, user: User, *, user_agent: str | None = None, ip_address: str | None = None
) -> tuple[str, str]:
    access_token = create_access_token(subject=user.id, extra_claims={"role": user.role.value})
    refresh_token = token_service.issue_refresh_token(
        db, user, user_agent=user_agent, ip_address=ip_address
    )
    return access_token, refresh_token


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def register_user(
    db: Session,
    payload: UserCreate,
    *,
    email_service: EmailService,
    user_agent: str | None = None,
    ip_address: str | None = None,
) -> tuple[User, str, str]:
    if get_user_by_email(db, payload.email):
        raise DuplicateUserError(f"Email '{payload.email}' is already registered")

    user = User(
        full_name=payload.full_name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.flush()  # populate user.id before issuing tokens tied to it

    verification_token = token_service.issue_email_verification_token(db, user)
    subject, body = build_verification_email(full_name=user.full_name, token=verification_token)
    email_service.send(to=user.email, subject=subject, body=body)

    access_token, refresh_token = _issue_token_pair(
        db, user, user_agent=user_agent, ip_address=ip_address
    )
    _log_audit(db, user_id=user.id, action=AuditAction.CREATE, ip_address=ip_address, details={"entity": "user"})

    db.commit()
    db.refresh(user)
    return user, access_token, refresh_token


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------


def authenticate_user(
    db: Session,
    email: str,
    password: str,
    *,
    user_agent: str | None = None,
    ip_address: str | None = None,
) -> tuple[User, str, str]:
    user = get_user_by_email(db, email)

    if user is None:
        # Deliberately identical error to "wrong password" — do not reveal
        # whether the email is registered.
        raise InvalidCredentialsError()

    if user.is_locked:
        retry_minutes = max(
            1, int((ensure_aware(user.locked_until) - datetime.now(timezone.utc)).total_seconds() // 60) + 1
        )
        raise AccountLockedError(retry_after_minutes=retry_minutes)

    if not user.is_active:
        raise AccountInactiveError()

    if not verify_password(password, user.hashed_password):
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= settings.MAX_FAILED_LOGIN_ATTEMPTS:
            user.locked_until = datetime.now(timezone.utc) + timedelta(
                minutes=settings.ACCOUNT_LOCKOUT_MINUTES
            )
            _log_audit(db, user_id=user.id, action=AuditAction.LOGIN_FAILED, ip_address=ip_address, details={"locked": True})
        else:
            _log_audit(db, user_id=user.id, action=AuditAction.LOGIN_FAILED, ip_address=ip_address, details=None)
        db.commit()
        raise InvalidCredentialsError()

    # Successful login: reset lockout counters, opportunistically upgrade
    # legacy bcrypt hashes to Argon2, record the login.
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = datetime.now(timezone.utc)
    if needs_rehash(user.hashed_password):
        user.hashed_password = hash_password(password)

    access_token, refresh_token = _issue_token_pair(
        db, user, user_agent=user_agent, ip_address=ip_address
    )
    _log_audit(db, user_id=user.id, action=AuditAction.LOGIN, ip_address=ip_address)

    db.commit()
    db.refresh(user)
    return user, access_token, refresh_token


# ---------------------------------------------------------------------------
# Token refresh / logout
# ---------------------------------------------------------------------------


def refresh_access_token(
    db: Session,
    raw_refresh_token: str,
    *,
    user_agent: str | None = None,
    ip_address: str | None = None,
) -> tuple[str, str]:
    """Validates the presented refresh token and rotates it: the old token
    is revoked, a new one is issued. Returns (new_access_token, new_refresh_token).
    """
    token_row = token_service.get_active_refresh_token(db, raw_refresh_token)
    if token_row is None:
        raise InvalidTokenError("This refresh token is invalid, expired, or has been revoked")

    user = token_row.user
    if user is None or not user.is_active or user.deleted_at is not None:
        raise InvalidTokenError()

    new_refresh_token = token_service.rotate_refresh_token(
        db, token_row, user_agent=user_agent, ip_address=ip_address
    )
    new_access_token = create_access_token(subject=user.id, extra_claims={"role": user.role.value})

    db.commit()
    return new_access_token, new_refresh_token


def logout_user(db: Session, raw_refresh_token: str) -> None:
    token_service.revoke_refresh_token(db, raw_refresh_token)
    db.commit()


# ---------------------------------------------------------------------------
# Forgot / reset / change password
# ---------------------------------------------------------------------------


def request_password_reset(db: Session, email: str, *, email_service: EmailService) -> None:
    """Always succeeds from the caller's perspective, whether or not the
    email is registered — prevents account enumeration via this endpoint."""
    user = get_user_by_email(db, email)
    if user is None:
        return

    raw_token = token_service.issue_password_reset_token(db, user)
    subject, body = build_password_reset_email(full_name=user.full_name, token=raw_token)
    email_service.send(to=user.email, subject=subject, body=body)
    db.commit()


def reset_password(db: Session, raw_token: str, new_password: str) -> None:
    token_row = token_service.consume_password_reset_token(db, raw_token)
    if token_row is None:
        raise InvalidTokenError("This password reset link is invalid or has expired")

    user = token_row.user
    user.hashed_password = hash_password(new_password)
    user.failed_login_attempts = 0
    user.locked_until = None
    token_service.revoke_all_refresh_tokens_for_user(db, user)
    _log_audit(db, user_id=user.id, action=AuditAction.UPDATE, details={"entity": "password_reset"})
    db.commit()


def change_password(db: Session, user: User, current_password: str, new_password: str) -> None:
    if not verify_password(current_password, user.hashed_password):
        raise InvalidCredentialsError()

    user.hashed_password = hash_password(new_password)
    token_service.revoke_all_refresh_tokens_for_user(db, user)
    _log_audit(db, user_id=user.id, action=AuditAction.UPDATE, details={"entity": "password_change"})
    db.commit()


# ---------------------------------------------------------------------------
# Email verification
# ---------------------------------------------------------------------------


def verify_email(db: Session, raw_token: str) -> None:
    token_row = token_service.consume_email_verification_token(db, raw_token)
    if token_row is None:
        raise InvalidTokenError("This verification link is invalid or has expired")

    user = token_row.user
    user.email_verified = True
    user.email_verified_at = datetime.now(timezone.utc)
    db.commit()


def resend_verification_email(db: Session, user: User, *, email_service: EmailService) -> None:
    if user.email_verified:
        return
    raw_token = token_service.issue_email_verification_token(db, user)
    subject, body = build_verification_email(full_name=user.full_name, token=raw_token)
    email_service.send(to=user.email, subject=subject, body=body)
    db.commit()
