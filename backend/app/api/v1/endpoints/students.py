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
from app.repositories.student import StudentRepository
from app.schemas.common import PaginatedResponse, PaginationParams, SortParams
from app.schemas.student import StudentCreate, StudentRead, StudentUpdate

router = APIRouter(prefix="/students", tags=["Students"])

_SORTABLE_FIELDS = {"enrollment_number", "grade_or_year", "created_at", "updated_at"}


@router.get(
    "",
    response_model=PaginatedResponse[StudentRead],
    dependencies=[Depends(require_permission(Permission.USERS_READ))],
)
def list_students(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    sort: SortParams = Depends(),
    search: str | None = Query(None, description="Search by enrollment number"),
    institution_id: UUID | None = Depends(resolve_institution_scope),
    department_id: UUID | None = Query(None),
    is_active: bool | None = Query(None),
) -> PaginatedResponse[StudentRead]:
    repo = StudentRepository(db)
    items, total = repo.list(
        pagination=pagination,
        sort=sort,
        allowed_sort_fields=_SORTABLE_FIELDS,
        search=search,
        search_fields=["enrollment_number"] if search else None,
        filters={"institution_id": institution_id, "department_id": department_id, "is_active": is_active},
    )
    return PaginatedResponse.build(
        [StudentRead.model_validate(s) for s in items], total_items=total, params=pagination
    )


@router.get("/{student_id}", response_model=StudentRead)
def get_student(
    student_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> StudentRead:
    repo = StudentRepository(db)
    student = repo.get_or_404(student_id)
    verify_object_institution_access(db, current_user, student.institution_id)
    return StudentRead.model_validate(student)


@router.post(
    "",
    response_model=StudentRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(Permission.USERS_MANAGE))],
)
def create_student(
    payload: StudentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> StudentRead:
    verify_object_institution_access(db, current_user, payload.institution_id)
    repo = StudentRepository(db)
    try:
        student = repo.create(payload.model_dump())
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateResourceError("This user already has a student profile") from exc
    db.refresh(student)
    return StudentRead.model_validate(student)


@router.patch(
    "/{student_id}",
    response_model=StudentRead,
    dependencies=[Depends(require_permission(Permission.USERS_MANAGE))],
)
def update_student(
    student_id: UUID,
    payload: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StudentRead:
    repo = StudentRepository(db)
    student = repo.get_or_404(student_id)
    verify_object_institution_access(db, current_user, student.institution_id)
    student = repo.update(student, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(student)
    return StudentRead.model_validate(student)


@router.delete(
    "/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission(Permission.USERS_MANAGE))],
)
def delete_student(
    student_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> None:
    repo = StudentRepository(db)
    student = repo.get_or_404(student_id)
    verify_object_institution_access(db, current_user, student.institution_id)
    repo.delete(student)
    db.commit()


@router.post(
    "/{student_id}/restore",
    response_model=StudentRead,
    dependencies=[Depends(require_permission(Permission.USERS_MANAGE))],
)
def restore_student(
    student_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> StudentRead:
    repo = StudentRepository(db)
    student = repo.get_deleted_or_404(student_id)
    verify_object_institution_access(db, current_user, student.institution_id)
    student = repo.restore(student)
    db.commit()
    db.refresh(student)
    return StudentRead.model_validate(student)
