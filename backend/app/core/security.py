"""Password hashing, JWT issuance/verification, and opaque token generation.

Three distinct "token" concepts live here, deliberately kept separate:
  1. JWT access/refresh tokens  — stateless-ish, carry claims, signed with
     SECRET_KEY. Refresh tokens are additionally tracked server-side (see
     app.models.refresh_token.RefreshToken) so they can be revoked.
  2. Opaque single-use tokens   — random strings for password-reset / email
     verification links. Never JWTs (no reason for claims), stored only as
     a SHA-256 hash (see hash_opaque_token), same rationale as passwords.
"""

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Argon2 is preferred for new hashes; bcrypt is kept as a verification
# fallback so any password hashed before this upgrade still authenticates.
# `deprecated="auto"` means passlib will re-hash a bcrypt password with
# Argon2 the next time verify_password succeeds, if the caller uses
# `needs_rehash` (see verify_and_upgrade_password below).
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def needs_rehash(hashed_password: str) -> bool:
    """True if the stored hash uses a deprecated scheme (e.g. bcrypt) and
    should be re-hashed with Argon2 next time the plaintext is available
    (i.e. right after a successful login)."""
    return pwd_context.needs_update(hashed_password)


# ---------------------------------------------------------------------------
# JWT access / refresh tokens
# ---------------------------------------------------------------------------


def create_access_token(subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode: dict[str, Any] = {
        "sub": subject,
        "type": TokenType.ACCESS.value,
        "iat": now,
        "exp": expire,
        "jti": str(uuid.uuid4()),
    }
    if extra_claims:
        to_encode.update(extra_claims)
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(subject: str, jti: str | None = None) -> tuple[str, str, datetime]:
    """Returns (encoded_jwt, jti, expires_at). The caller persists a
    RefreshToken row keyed by a hash of the returned JWT (see
    hash_opaque_token) — the `jti` claim is redundant with that DB row's id
    when jti == str(row.id), which callers should arrange so a presented
    token can be looked up directly by its claim without depending on the
    hash lookup alone.
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    token_id = jti or str(uuid.uuid4())
    to_encode: dict[str, Any] = {
        "sub": subject,
        "type": TokenType.REFRESH.value,
        "iat": now,
        "exp": expire,
        "jti": token_id,
    }
    encoded = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded, token_id, expire


def decode_token(token: str, expected_type: TokenType | None = None) -> dict[str, Any] | None:
    """Decodes and validates a JWT's signature/expiry. If `expected_type` is
    given, also enforces the `type` claim matches (prevents an access token
    being replayed where a refresh token is expected, and vice versa)."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None

    if expected_type is not None and payload.get("type") != expected_type.value:
        return None

    return payload


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Kept for backward compatibility with existing callers (app.api.deps)."""
    return decode_token(token, expected_type=TokenType.ACCESS)


# ---------------------------------------------------------------------------
# Opaque single-use tokens (refresh / password-reset / email-verification)
# ---------------------------------------------------------------------------


def generate_opaque_token() -> str:
    """A cryptographically random, URL-safe token for links sent out of
    band (email). ~256 bits of entropy."""
    return secrets.token_urlsafe(32)


def hash_opaque_token(raw_token: str) -> str:
    """SHA-256 is sufficient (not bcrypt/argon2) here: the input is already
    high-entropy random data, not a low-entropy human password, so there's
    no offline brute-force risk to slow down — we just need a fast,
    deterministic lookup key that doesn't store the raw secret."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
