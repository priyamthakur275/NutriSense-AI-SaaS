from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise credentials_exception

    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user or not user.is_active or user.deleted_at is not None:
        raise credentials_exception

    # A previously-issued access token is still cryptographically valid even
    # after the account is subsequently locked — check live state, not just
    # what the token claims to be true.
    if user.is_locked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is temporarily locked",
        )

    return user


def get_current_verified_user(current_user: User = Depends(get_current_user)) -> User:
    """Use on routes that require a confirmed email address, in addition to
    a valid session (e.g. anything that sends notifications to that email)."""
    if not current_user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email address to access this resource",
        )
    return current_user


def require_roles(*allowed_roles: UserRole) -> Callable[[User], User]:
    """Dependency factory enforcing role-based access control on a route.

    For fine-grained (permission-level, not just role-level) checks, prefer
    `app.api.rbac.require_permission` instead.
    """

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return current_user

    return role_checker
