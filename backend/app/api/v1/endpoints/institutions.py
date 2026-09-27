from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.rbac import Permission, require_permission, require_roles
from app.api.tenant_scope import verify_institution_scope
from app.db.session import get_db
from app.models.enums import InstitutionType
from app.models.user import UserRole
from app.repositories.institution import InstitutionRepository
from app.schemas.common import PaginatedResponse, PaginationParams, SortParams
from app.schemas.institution import InstitutionCreate, InstitutionRead, InstitutionUpdate

router = APIRouter(prefix="/institutions", tags=["Institutions"])

_SORTABLE_FIELDS = {"name", "type", "city", "created_at", "updated_at"}


@router.get("", response_model=PaginatedResponse[InstitutionRead])
def list_institutions(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    sort: SortParams = Depends(),
    search: str | None = Query(None, description="Search by institution name"),
    type: InstitutionType | None = Query(None, description="Filter by institution type"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    _current_user=Depends(get_current_user),
) -> PaginatedResponse[InstitutionRead]:
    repo = InstitutionRepository(db)
    items, total = repo.list(
        pagination=pagination,
        sort=sort,
        allowed_sort_fields=_SORTABLE_FIELDS,
        search=search,
        search_fields=["name"] if search else None,
        filters={"type": type, "is_active": is_active},
    )
    return PaginatedResponse.build(
        [InstitutionRead.model_validate(i) for i in items], total_items=total, params=pagination
    )


@router.get("/{institution_id}", response_model=InstitutionRead)
def get_institution(
    institution_id: UUID = Depends(verify_institution_scope), db: Session = Depends(get_db)
) -> InstitutionRead:
    repo = InstitutionRepository(db)
    return InstitutionRead.model_validate(repo.get_or_404(institution_id))


@router.post(
    "",
    response_model=InstitutionRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.SUPER_ADMIN))],
)
def create_institution(payload: InstitutionCreate, db: Session = Depends(get_db)) -> InstitutionRead:
    repo = InstitutionRepository(db)
    institution = repo.create(payload.model_dump())
    db.commit()
    db.refresh(institution)
    return InstitutionRead.model_validate(institution)


@router.patch(
    "/{institution_id}",
    response_model=InstitutionRead,
    dependencies=[Depends(require_permission(Permission.INSTITUTION_MANAGE))],
)
def update_institution(
    payload: InstitutionUpdate,
    institution_id: UUID = Depends(verify_institution_scope),
    db: Session = Depends(get_db),
) -> InstitutionRead:
    repo = InstitutionRepository(db)
    institution = repo.get_or_404(institution_id)
    institution = repo.update(institution, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(institution)
    return InstitutionRead.model_validate(institution)


@router.delete(
    "/{institution_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission(Permission.INSTITUTION_MANAGE))],
)
def delete_institution(
    institution_id: UUID = Depends(verify_institution_scope), db: Session = Depends(get_db)
) -> None:
    """Soft-delete only — see BaseRepository.delete(). Institutions are
    never hard-deleted via the API; historical data (past meals, reports)
    must remain queryable."""
    repo = InstitutionRepository(db)
    institution = repo.get_or_404(institution_id)
    repo.delete(institution)
    db.commit()


@router.post(
    "/{institution_id}/restore",
    response_model=InstitutionRead,
    dependencies=[Depends(require_permission(Permission.INSTITUTION_MANAGE))],
)
def restore_institution(
    institution_id: UUID = Depends(verify_institution_scope), db: Session = Depends(get_db)
) -> InstitutionRead:
    """Reverses a soft-delete — corrects an accidental deactivation without
    losing the institution's history (departments, past meals, reports all
    remain linked throughout, since soft delete never removed the row)."""
    repo = InstitutionRepository(db)
    institution = repo.get_deleted_or_404(institution_id)
    institution = repo.restore(institution)
    db.commit()
    db.refresh(institution)
    return InstitutionRead.model_validate(institution)
