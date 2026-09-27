from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.rbac import Permission, require_permission
from app.api.tenant_scope import verify_object_institution_access
from app.core.exceptions import DuplicateResourceError, NotFoundError
from app.db.session import get_db
from app.models.student import Student
from app.models.user import User
from app.repositories.parent_student_link import ParentStudentLinkRepository
from app.schemas.common import PaginatedResponse, PaginationParams
from app.schemas.parent_student_link import ParentStudentLinkCreate, ParentStudentLinkRead

router = APIRouter(prefix="/parent-links", tags=["Parent Links"])


@router.get("/me", response_model=list[ParentStudentLinkRead])
def list_my_linked_children(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[ParentStudentLinkRead]:
    """A parent's self-service view of every child they're linked to — no
    special permission required beyond being authenticated, since this
    only ever returns the caller's own links."""
    repo = ParentStudentLinkRepository(db)
    items, _ = repo.list(
        pagination=PaginationParams(page=1, page_size=100),
        filters={"parent_user_id": current_user.id},
    )
    return [ParentStudentLinkRead.model_validate(link) for link in items]


@router.get(
    "",
    response_model=PaginatedResponse[ParentStudentLinkRead],
    dependencies=[Depends(require_permission(Permission.USERS_READ))],
)
def list_parent_links(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    student_id: UUID | None = Query(None),
    parent_user_id: str | None = Query(None),
) -> PaginatedResponse[ParentStudentLinkRead]:
    repo = ParentStudentLinkRepository(db)
    items, total = repo.list(
        pagination=pagination,
        filters={"student_id": student_id, "parent_user_id": parent_user_id},
    )
    return PaginatedResponse.build(
        [ParentStudentLinkRead.model_validate(link) for link in items], total_items=total, params=pagination
    )


@router.post(
    "",
    response_model=ParentStudentLinkRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(Permission.USERS_MANAGE))],
)
def create_parent_link(
    payload: ParentStudentLinkCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> ParentStudentLinkRead:
    student = db.query(Student).filter(Student.id == payload.student_id).first()
    if student is None:
        raise NotFoundError(f"Student '{payload.student_id}' not found")
    # Scoped via the STUDENT's institution — an Institution Admin can only
    # link parents to students within their own institution, never another.
    verify_object_institution_access(db, current_user, student.institution_id)

    repo = ParentStudentLinkRepository(db)
    try:
        link = repo.create(payload.model_dump())
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateResourceError("This parent is already linked to this student") from exc
    db.refresh(link)
    return ParentStudentLinkRead.model_validate(link)


@router.delete(
    "/{link_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission(Permission.USERS_MANAGE))],
)
def delete_parent_link(
    link_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> None:
    repo = ParentStudentLinkRepository(db)
    link = repo.get_or_404(link_id)
    student = db.query(Student).filter(Student.id == link.student_id).first()
    if student is not None:
        verify_object_institution_access(db, current_user, student.institution_id)
    repo.delete(link, hard=True)  # ParentStudentLink has no soft-delete column
    db.commit()
