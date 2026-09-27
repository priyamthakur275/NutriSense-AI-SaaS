from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.rbac import Permission, require_permission
from app.core.exceptions import DuplicateResourceError
from app.db.session import get_db
from app.models.enums import AttendanceMethod
from app.models.user import User
from app.repositories.attendance import AttendanceRepository
from app.schemas.attendance import AttendanceCreate, AttendanceRead
from app.schemas.common import PaginatedResponse, PaginationParams, SortParams

router = APIRouter(prefix="/attendance", tags=["Attendance"])

_SORTABLE_FIELDS = {"attended_at"}


@router.get(
    "",
    response_model=PaginatedResponse[AttendanceRead],
    dependencies=[Depends(require_permission(Permission.ATTENDANCE_READ))],
)
def list_attendance(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    sort: SortParams = Depends(),
    user_id: str | None = Query(None),
    meal_id: UUID | None = Query(None),
    method: AttendanceMethod | None = Query(None),
) -> PaginatedResponse[AttendanceRead]:
    repo = AttendanceRepository(db)
    items, total = repo.list(
        pagination=pagination,
        sort=sort,
        allowed_sort_fields=_SORTABLE_FIELDS,
        default_sort_field="attended_at",
        filters={"user_id": user_id, "meal_id": meal_id, "method": method},
    )
    return PaginatedResponse.build(
        [AttendanceRead.model_validate(a) for a in items], total_items=total, params=pagination
    )


@router.get(
    "/{attendance_id}",
    response_model=AttendanceRead,
    dependencies=[Depends(require_permission(Permission.ATTENDANCE_READ))],
)
def get_attendance(attendance_id: UUID, db: Session = Depends(get_db)) -> AttendanceRead:
    repo = AttendanceRepository(db)
    return AttendanceRead.model_validate(repo.get_or_404(attendance_id))


@router.post(
    "",
    response_model=AttendanceRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(Permission.ATTENDANCE_RECORD))],
)
def create_attendance(payload: AttendanceCreate, db: Session = Depends(get_db)) -> AttendanceRead:
    """A user can only be marked present for a given meal once — enforced by
    a unique (user_id, meal_id) constraint, surfaced here as a 409 rather
    than a generic 500."""
    repo = AttendanceRepository(db)
    try:
        record = repo.create(payload.model_dump())
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateResourceError("This user is already marked present for this meal") from exc
    db.refresh(record)
    return AttendanceRead.model_validate(record)


@router.delete(
    "/{attendance_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission(Permission.ATTENDANCE_RECORD))],
)
def delete_attendance(attendance_id: UUID, db: Session = Depends(get_db)) -> None:
    """Attendance has no soft-delete or update support by design (it's an
    immutable fact about a point in time) — only create and hard-delete
    (for correcting a mis-scan) are exposed."""
    repo = AttendanceRepository(db)
    record = repo.get_or_404(attendance_id)
    repo.delete(record)
    db.commit()
