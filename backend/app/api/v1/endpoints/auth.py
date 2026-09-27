from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.rate_limit import RateLimiter
from app.core.security import TokenType, decode_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LogoutRequest,
    MessageResponse,
    RefreshRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
)
from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserPublic
from app.services import auth_service
from app.services.email_service import get_email_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _to_public_user(user: User) -> UserPublic:
    return UserPublic(id=user.id, email=user.email, fullName=user.full_name, role=user.role)


def _client_meta(request: Request) -> tuple[str | None, str | None]:
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None
    return user_agent, ip_address


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=3, seconds=60, scope="register"))],
)
def register(payload: UserCreate, request: Request, db: Session = Depends(get_db)) -> TokenResponse:
    """Creates a new account, issues an access/refresh token pair, and sends
    a (mocked) email-verification link. The account is usable immediately —
    email verification gates specific actions, not login itself."""
    user_agent, ip_address = _client_meta(request)
    user, access_token, refresh_token = auth_service.register_user(
        db, payload, email_service=get_email_service(), user_agent=user_agent, ip_address=ip_address
    )
    return TokenResponse(access_token=access_token, refresh_token=refresh_token, user=_to_public_user(user))


@router.post(
    "/login",
    response_model=TokenResponse,
    dependencies=[Depends(RateLimiter(times=5, seconds=60, scope="login"))],
)
def login(payload: UserLogin, request: Request, db: Session = Depends(get_db)) -> TokenResponse:
    user_agent, ip_address = _client_meta(request)
    user, access_token, refresh_token = auth_service.authenticate_user(
        db, payload.email, payload.password, user_agent=user_agent, ip_address=ip_address
    )
    return TokenResponse(access_token=access_token, refresh_token=refresh_token, user=_to_public_user(user))


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, request: Request, db: Session = Depends(get_db)) -> TokenResponse:
    """Rotates a refresh token: the presented token is revoked and a new
    access/refresh pair is issued. The old token can never be used again —
    presenting it a second time is treated as invalid, not silently ignored."""
    user_agent, ip_address = _client_meta(request)
    access_token, new_refresh_token = auth_service.refresh_access_token(
        db, payload.refresh_token, user_agent=user_agent, ip_address=ip_address
    )
    # Re-fetch the user for the response body via the new token's subject.
    token_payload = decode_token(access_token, expected_type=TokenType.ACCESS)
    user = db.query(User).filter(User.id == token_payload["sub"]).first()
    return TokenResponse(access_token=access_token, refresh_token=new_refresh_token, user=_to_public_user(user))


@router.post("/logout", response_model=MessageResponse)
def logout(payload: LogoutRequest, db: Session = Depends(get_db)) -> MessageResponse:
    """Revokes the given refresh token. Logout is intentionally not
    authenticated by access token alone — only the refresh token being
    revoked is required, so logout still works even with an expired access
    token (a common real-world case: the access token already lapsed by the
    time the user clicks "log out")."""
    auth_service.logout_user(db, payload.refresh_token)
    return MessageResponse(message="Logged out successfully")


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)) -> MessageResponse:
    auth_service.request_password_reset(db, payload.email, email_service=get_email_service())
    # Always the same response, whether or not the email is registered.
    return MessageResponse(
        message="If an account with that email exists, a password reset link has been sent."
    )


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)) -> MessageResponse:
    auth_service.reset_password(db, payload.token, payload.new_password)
    return MessageResponse(message="Password reset successfully. Please sign in with your new password.")


@router.post("/change-password", response_model=MessageResponse)
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    auth_service.change_password(db, current_user, payload.current_password, payload.new_password)
    return MessageResponse(message="Password changed successfully. Please sign in again.")


@router.post("/verify-email", response_model=MessageResponse)
def verify_email(payload: VerifyEmailRequest, db: Session = Depends(get_db)) -> MessageResponse:
    auth_service.verify_email(db, payload.token)
    return MessageResponse(message="Email verified successfully.")


@router.post("/resend-verification", response_model=MessageResponse)
def resend_verification(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> MessageResponse:
    auth_service.resend_verification_email(db, current_user, email_service=get_email_service())
    return MessageResponse(message="If your email isn't already verified, a new link has been sent.")
