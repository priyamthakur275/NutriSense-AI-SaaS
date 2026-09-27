from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.rbac import Permission, require_permission
from app.api.tenant_scope import resolve_institution_scope, verify_object_institution_access
from app.core.exceptions import DuplicateResourceError
from app.db.session import get_db
from app.models.user import User
from app.repositories.staff import StaffRepository
from app.schemas.common import PaginatedResponse, PaginationParams, SortParams
from app.schemas.staff import StaffCreate, StaffRead, StaffUpdate

router = APIRouter(prefix="/staff", tags=["Staff"])

_SORTABLE_FIELDS = {"employee_id", "job_title", "created_at", "updated_at"}


@router.get(
    "",
    response_model=PaginatedResponse[StaffRead],
    dependencies=[Depends(require_permission(Permission.USERS_READ))],
)
def list_staff(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    sort: SortParams = Depends(),
    search: str | None = Query(None, description="Search by employee ID or job title"),
    institution_id: UUID | None = Depends(resolve_institution_scope),
    department_id: UUID | None = Query(None),
    is_active: bool | None = Query(None),
) -> PaginatedResponse[StaffRead]:
    repo = StaffRepository(db)
    items, total = repo.list(
        pagination=pagination,
        sort=sort,
        allowed_sort_fields=_SORTABLE_FIELDS,
        search=search,
        search_fields=["employee_id", "job_title"] if search else None,
        filters={"institution_id": institution_id, "department_id": department_id, "is_active": is_active},
    )
    return PaginatedResponse.build(
        [StaffRead.model_validate(s) for s in items], total_items=total, params=pagination
    )


@router.get("/{staff_id}", response_model=StaffRead)
def get_staff(
    staff_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> StaffRead:
    repo = StaffRepository(db)
    staff = repo.get_or_404(staff_id)
    verify_object_institution_access(db, current_user, staff.institution_id)
    return StaffRead.model_validate(staff)


@router.post(
    "",
    response_model=StaffRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(Permission.USERS_MANAGE))],
)
def create_staff(
    payload: StaffCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> StaffRead:
    verify_object_institution_access(db, current_user, payload.institution_id)
    repo = StaffRepository(db)
    try:
        staff = repo.create(payload.model_dump())
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateResourceError("This user already has a staff profile") from exc
    db.refresh(staff)
    return StaffRead.model_validate(staff)


@router.patch(
    "/{staff_id}",
    response_model=StaffRead,
    dependencies=[Depends(require_permission(Permission.USERS_MANAGE))],
)
def update_staff(
    staff_id: UUID, payload: StaffUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> StaffRead:
    repo = StaffRepository(db)
    staff = repo.get_or_404(staff_id)
    verify_object_institution_access(db, current_user, staff.institution_id)
    staff = repo.update(staff, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(staff)
    return StaffRead.model_validate(staff)


@router.delete(
    "/{staff_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission(Permission.USERS_MANAGE))],
)
def delete_staff(
    staff_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> None:
    repo = StaffRepository(db)
    staff = repo.get_or_404(staff_id)
    verify_object_institution_access(db, current_user, staff.institution_id)
    repo.delete(staff)
    db.commit()


@router.post(
    "/{staff_id}/restore",
    response_model=StaffRead,
    dependencies=[Depends(require_permission(Permission.USERS_MANAGE))],
)
def restore_staff(
    staff_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> StaffRead:
    repo = StaffRepository(db)
    staff = repo.get_deleted_or_404(staff_id)
    verify_object_institution_access(db, current_user, staff.institution_id)
    staff = repo.restore(staff)
    db.commit()
    db.refresh(staff)
    return StaffRead.model_validate(staff)
