from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.rbac import Permission, require_permission
from app.api.tenant_scope import resolve_institution_scope, verify_object_institution_access
from app.db.session import get_db
from app.models.user import User
from app.repositories.announcement import AnnouncementRepository
from app.schemas.announcement import AnnouncementCreate, AnnouncementRead
from app.schemas.common import PaginatedResponse, PaginationParams
from app.services import announcement_service

router = APIRouter(prefix="/announcements", tags=["Announcements"])

_SORTABLE_FIELDS = {"created_at", "audience"}


@router.get("", response_model=PaginatedResponse[AnnouncementRead])
def list_announcements(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    institution_id: UUID | None = Depends(resolve_institution_scope),
    _current_user: User = Depends(get_current_user),
) -> PaginatedResponse[AnnouncementRead]:
    repo = AnnouncementRepository(db)
    items, total = repo.list(
        pagination=pagination,
        default_sort_field="created_at",
        allowed_sort_fields=_SORTABLE_FIELDS,
        filters={"institution_id": institution_id},
    )
    return PaginatedResponse.build(
        [AnnouncementRead.model_validate(a) for a in items], total_items=total, params=pagination
    )


@router.post(
    "",
    response_model=AnnouncementRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(Permission.USERS_MANAGE))],
)
async def create_announcement(
    payload: AnnouncementCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> AnnouncementRead:
    """Broadcasts to the resolved audience by fanning out to the existing
    Notification table — see app.services.announcement_service. Requires
    `users:manage` (the same permission that gates managing accounts) since
    a broadcast reaches every matching user's inbox at once."""
    verify_object_institution_access(db, current_user, payload.institution_id)
    announcement = await announcement_service.send_announcement(db, payload, created_by=current_user)
    return AnnouncementRead.model_validate(announcement)
