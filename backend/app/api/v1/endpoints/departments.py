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
from app.repositories.department import DepartmentRepository
from app.schemas.common import PaginatedResponse, PaginationParams, SortParams
from app.schemas.department import DepartmentCreate, DepartmentRead, DepartmentUpdate

router = APIRouter(prefix="/departments", tags=["Departments"])

_SORTABLE_FIELDS = {"name", "code", "created_at", "updated_at"}


@router.get("", response_model=PaginatedResponse[DepartmentRead])
def list_departments(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    sort: SortParams = Depends(),
    search: str | None = Query(None, description="Search by department name"),
    institution_id: UUID | None = Depends(resolve_institution_scope),
    _current_user: User = Depends(get_current_user),
) -> PaginatedResponse[DepartmentRead]:
    repo = DepartmentRepository(db)
    items, total = repo.list(
        pagination=pagination,
        sort=sort,
        allowed_sort_fields=_SORTABLE_FIELDS,
        search=search,
        search_fields=["name"] if search else None,
        filters={"institution_id": institution_id},
    )
    return PaginatedResponse.build(
        [DepartmentRead.model_validate(d) for d in items], total_items=total, params=pagination
    )


@router.get("/{department_id}", response_model=DepartmentRead)
def get_department(
    department_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> DepartmentRead:
    repo = DepartmentRepository(db)
    department = repo.get_or_404(department_id)
    verify_object_institution_access(db, current_user, department.institution_id)
    return DepartmentRead.model_validate(department)


@router.post(
    "",
    response_model=DepartmentRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(Permission.DEPARTMENT_MANAGE))],
)
def create_department(
    payload: DepartmentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> DepartmentRead:
    verify_object_institution_access(db, current_user, payload.institution_id)
    repo = DepartmentRepository(db)
    try:
        department = repo.create(payload.model_dump())
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateResourceError(
            f"A department with code '{payload.code}' already exists for this institution"
        ) from exc
    db.refresh(department)
    return DepartmentRead.model_validate(department)


@router.patch(
    "/{department_id}",
    response_model=DepartmentRead,
    dependencies=[Depends(require_permission(Permission.DEPARTMENT_MANAGE))],
)
def update_department(
    department_id: UUID,
    payload: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DepartmentRead:
    repo = DepartmentRepository(db)
    department = repo.get_or_404(department_id)
    verify_object_institution_access(db, current_user, department.institution_id)
    try:
        department = repo.update(department, payload.model_dump(exclude_unset=True))
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateResourceError("A department with this code already exists for this institution") from exc
    db.refresh(department)
    return DepartmentRead.model_validate(department)


@router.delete(
    "/{department_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission(Permission.DEPARTMENT_MANAGE))],
)
def delete_department(
    department_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> None:
    repo = DepartmentRepository(db)
    department = repo.get_or_404(department_id)
    verify_object_institution_access(db, current_user, department.institution_id)
    repo.delete(department)
    db.commit()
