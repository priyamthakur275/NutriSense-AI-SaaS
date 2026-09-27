from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.rbac import Permission, require_permission
from app.api.tenant_scope import verify_institution_scope
from app.db.session import get_db
from app.repositories.institution_settings import InstitutionSettingsRepository
from app.schemas.institution_settings import InstitutionSettingsRead, InstitutionSettingsUpdate
from app.services import institution_settings_service

router = APIRouter(prefix="/institutions/{institution_id}/settings", tags=["Institution Settings"])


@router.get("", response_model=InstitutionSettingsRead)
def get_institution_settings(
    institution_id: UUID = Depends(verify_institution_scope), db: Session = Depends(get_db)
) -> InstitutionSettingsRead:
    settings = institution_settings_service.get_or_create_settings(db, institution_id)
    return InstitutionSettingsRead.model_validate(settings)


@router.patch(
    "",
    response_model=InstitutionSettingsRead,
    dependencies=[Depends(require_permission(Permission.INSTITUTION_MANAGE))],
)
def update_institution_settings(
    payload: InstitutionSettingsUpdate,
    institution_id: UUID = Depends(verify_institution_scope),
    db: Session = Depends(get_db),
) -> InstitutionSettingsRead:
    repo = InstitutionSettingsRepository(db)
    settings = institution_settings_service.get_or_create_settings(db, institution_id)
    settings = repo.update(settings, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(settings)
    return InstitutionSettingsRead.model_validate(settings)
