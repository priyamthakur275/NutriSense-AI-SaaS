from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.rbac import Permission, require_permission
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.user import User
from app.models.user_settings import UserSettings
from app.repositories.user_settings import UserSettingsRepository
from app.schemas.user_settings import UserSettingsRead, UserSettingsUpdate
from app.services import user_settings_service

router = APIRouter(prefix="/user-settings", tags=["User Settings"])


@router.get("/me", response_model=UserSettingsRead)
def get_my_settings(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> UserSettingsRead:
    settings = user_settings_service.get_or_create_settings(db, current_user)
    return UserSettingsRead.model_validate(settings)


@router.patch("/me", response_model=UserSettingsRead)
def update_my_settings(
    payload: UserSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserSettingsRead:
    repo = UserSettingsRepository(db)
    settings = user_settings_service.get_or_create_settings(db, current_user)
    settings = repo.update(settings, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(settings)
    return UserSettingsRead.model_validate(settings)


@router.get(
    "/{user_id}",
    response_model=UserSettingsRead,
    dependencies=[Depends(require_permission(Permission.USERS_READ))],
)
def get_user_settings(user_id: str, db: Session = Depends(get_db)) -> UserSettingsRead:
    """Admin/support access to another user's settings — e.g. diagnosing a
    notification-preference complaint. Does not auto-create: if the target
    user has never touched their settings, this 404s rather than
    fabricating a row on their behalf."""
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if settings is None:
        raise NotFoundError(f"No settings found for user '{user_id}'")
    return UserSettingsRead.model_validate(settings)
