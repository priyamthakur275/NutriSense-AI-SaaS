"""Lazy get-or-create for NutritionProfile — identical rationale and
pattern to app.services.user_settings_service: a user may never fill this
in, so no row should exist until they (or the recommendation engine, on
their behalf) first touches it."""

from sqlalchemy.orm import Session

from app.models.nutrition_profile import NutritionProfile
from app.models.user import User
from app.repositories.nutrition_profile import NutritionProfileRepository


def get_or_create_profile(db: Session, user: User) -> NutritionProfile:
    existing = db.query(NutritionProfile).filter(NutritionProfile.user_id == user.id).first()
    if existing is not None:
        return existing

    repo = NutritionProfileRepository(db)
    profile = repo.create({"user_id": user.id})
    db.commit()
    db.refresh(profile)
    return profile
