"""Custom exception hierarchy for authentication/authorization, plus the
FastAPI exception handlers that translate them into consistent JSON
responses. Registered onto the app in main.py.

Using dedicated exception classes (rather than raising HTTPException
directly from services) keeps the service layer free of any HTTP-specific
concerns — a service can be reused by a future non-HTTP caller (a CLI
script, a background job) without dragging FastAPI into its imports.
"""

from __future__ import annotations

from fastapi import Request, status
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base class for all application-raised errors that should be
    translated into an HTTP response by a registered handler."""

    status_code: int = status.HTTP_400_BAD_REQUEST
    error_code: str = "app_error"

    def __init__(self, message: str, *, error_code: str | None = None) -> None:
        self.message = message
        if error_code:
            self.error_code = error_code
        super().__init__(message)


class AuthenticationError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "authentication_failed"


class InvalidCredentialsError(AuthenticationError):
    error_code = "invalid_credentials"

    def __init__(self) -> None:
        super().__init__("Incorrect email or password")


class AccountLockedError(AuthenticationError):
    error_code = "account_locked"

    def __init__(self, retry_after_minutes: int) -> None:
        self.retry_after_minutes = retry_after_minutes
        super().__init__(
            f"Account temporarily locked due to repeated failed login attempts. "
            f"Try again in {retry_after_minutes} minute(s)."
        )


class AccountInactiveError(AuthenticationError):
    error_code = "account_inactive"

    def __init__(self) -> None:
        super().__init__("This account has been deactivated")


class EmailNotVerifiedError(AuthenticationError):
    error_code = "email_not_verified"

    def __init__(self) -> None:
        super().__init__("Please verify your email address before signing in")


class TokenError(AuthenticationError):
    error_code = "invalid_token"


class TokenExpiredError(TokenError):
    error_code = "token_expired"

    def __init__(self) -> None:
        super().__init__("This token has expired")


class TokenRevokedError(TokenError):
    error_code = "token_revoked"

    def __init__(self) -> None:
        super().__init__("This token has been revoked")


class InvalidTokenError(TokenError):
    error_code = "invalid_token"

    def __init__(self, message: str = "Invalid or malformed token") -> None:
        super().__init__(message)


class AuthorizationError(AppError):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "forbidden"

    def __init__(self, message: str = "You do not have permission to perform this action") -> None:
        super().__init__(message)


class DuplicateResourceError(AppError):
    status_code = status.HTTP_409_CONFLICT
    error_code = "duplicate_resource"


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "not_found"


class ValidationAppError(AppError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "validation_error"


class RateLimitExceededError(AppError):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    error_code = "rate_limit_exceeded"

    def __init__(self, retry_after_seconds: int) -> None:
        self.retry_after_seconds = retry_after_seconds
        super().__init__(f"Too many requests. Try again in {retry_after_seconds} second(s).")


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    headers = {}
    if isinstance(exc, RateLimitExceededError):
        headers["Retry-After"] = str(exc.retry_after_seconds)

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "error_code": exc.error_code},
        headers=headers or None,
    )


def register_exception_handlers(app) -> None:  # noqa: ANN001 - FastAPI app instance
    app.add_exception_handler(AppError, app_error_handler)
