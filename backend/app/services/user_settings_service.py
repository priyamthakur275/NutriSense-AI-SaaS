"""Lazy get-or-create for UserSettings: per the model's own docstring, a
user may have no settings row until they first change one. This is the
only piece of logic beyond plain field assignment for this resource.
"""

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.user_settings import UserSettings
from app.repositories.user_settings import UserSettingsRepository


def get_or_create_settings(db: Session, user: User) -> UserSettings:
    repo = UserSettingsRepository(db)
    existing = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    if existing is not None:
        return existing

    settings = repo.create({"user_id": user.id})
    db.commit()
    db.refresh(settings)
    return settings
