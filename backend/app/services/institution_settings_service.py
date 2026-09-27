"""Lazy get-or-create for InstitutionSettings — same pattern as
user_settings_service / nutrition_profile_service: an institution may
never touch its settings, so no row should exist until it's first read or
written."""

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.institution_settings import InstitutionSettings
from app.repositories.institution_settings import InstitutionSettingsRepository


def get_or_create_settings(db: Session, institution_id: UUID) -> InstitutionSettings:
    existing = (
        db.query(InstitutionSettings)
        .filter(InstitutionSettings.institution_id == institution_id)
        .first()
    )
    if existing is not None:
        return existing

    repo = InstitutionSettingsRepository(db)
    settings = repo.create({"institution_id": institution_id})
    db.commit()
    db.refresh(settings)
    return settings
