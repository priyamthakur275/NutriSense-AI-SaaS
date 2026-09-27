"""Email delivery abstraction.

`EmailService` is the interface every call site depends on. In development
(and in this scaffold), `ConsoleEmailService` just logs the message — no
external provider is wired up. Swapping in a real provider (SES, SendGrid,
Postmark) means writing one more class that implements `send()` and
constructing that instead in `get_email_service()`; nothing else changes.
"""

from __future__ import annotations

from typing import Protocol

from app.core.logging import get_logger

logger = get_logger(__name__)


class EmailService(Protocol):
    def send(self, *, to: str, subject: str, body: str) -> None: ...


class ConsoleEmailService:
    """Mock provider: logs the email instead of sending it. Sufficient for
    local development and for verifying the auth flow end-to-end without a
    real mail provider configured."""

    def send(self, *, to: str, subject: str, body: str) -> None:
        logger.info("=== MOCK EMAIL ===\nTo: %s\nSubject: %s\n\n%s\n==================", to, subject, body)


def get_email_service() -> EmailService:
    return ConsoleEmailService()


def build_verification_email(*, full_name: str, token: str) -> tuple[str, str]:
    subject = "Verify your NutriSense AI email"
    body = (
        f"Hi {full_name},\n\n"
        f"Please verify your email address using this token:\n\n{token}\n\n"
        f"This link expires shortly. If you didn't create an account, ignore this email."
    )
    return subject, body


def build_password_reset_email(*, full_name: str, token: str) -> tuple[str, str]:
    subject = "Reset your NutriSense AI password"
    body = (
        f"Hi {full_name},\n\n"
        f"Use this token to reset your password:\n\n{token}\n\n"
        f"If you didn't request this, you can safely ignore this email — "
        f"your password will not be changed."
    )
    return subject, body


def build_invite_email(*, institution_name: str, role: str, token: str) -> tuple[str, str]:
    subject = f"You've been invited to join {institution_name} on NutriSense AI"
    body = (
        f"You've been invited to join {institution_name} as a {role}.\n\n"
        f"Use this invitation token to complete your registration:\n\n{token}\n\n"
        f"This invitation expires soon. If you weren't expecting this, "
        f"you can safely ignore this email."
    )
    return subject, body
