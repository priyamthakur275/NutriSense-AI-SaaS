from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.rbac import Permission, has_permission, require_permission
from app.db.session import get_db
from app.models.enums import NotificationType
from app.models.user import User
from app.repositories.notification import NotificationRepository
from app.schemas.common import PaginatedResponse, PaginationParams, SortParams
from app.schemas.notification import NotificationCreate, NotificationRead, NotificationUpdate

router = APIRouter(prefix="/notifications", tags=["Notifications"])

_SORTABLE_FIELDS = {"created_at", "is_read"}


def _require_owner_or_permission(notification, current_user: User, permission: Permission) -> None:
    if notification.user_id != current_user.id and not has_permission(current_user.role, permission):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your notification")


@router.get("/me", response_model=PaginatedResponse[NotificationRead])
def list_my_notifications(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    sort: SortParams = Depends(),
    is_read: bool | None = Query(None),
    type: NotificationType | None = Query(None),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse[NotificationRead]:
    repo = NotificationRepository(db)
    items, total = repo.list(
        pagination=pagination,
        sort=sort,
        allowed_sort_fields=_SORTABLE_FIELDS,
        filters={"user_id": current_user.id, "is_read": is_read, "type": type},
    )
    return PaginatedResponse.build(
        [NotificationRead.model_validate(n) for n in items], total_items=total, params=pagination
    )


@router.get(
    "",
    response_model=PaginatedResponse[NotificationRead],
    dependencies=[Depends(require_permission(Permission.USERS_READ))],
)
def list_notifications(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    sort: SortParams = Depends(),
    user_id: str | None = Query(None, description="Filter by recipient"),
    is_read: bool | None = Query(None),
) -> PaginatedResponse[NotificationRead]:
    repo = NotificationRepository(db)
    items, total = repo.list(
        pagination=pagination,
        sort=sort,
        allowed_sort_fields=_SORTABLE_FIELDS,
        filters={"user_id": user_id, "is_read": is_read},
    )
    return PaginatedResponse.build(
        [NotificationRead.model_validate(n) for n in items], total_items=total, params=pagination
    )


@router.get("/{notification_id}", response_model=NotificationRead)
def get_notification(
    notification_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> NotificationRead:
    repo = NotificationRepository(db)
    notification = repo.get_or_404(notification_id)
    _require_owner_or_permission(notification, current_user, Permission.USERS_READ)
    return NotificationRead.model_validate(notification)


@router.post(
    "",
    response_model=NotificationRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(Permission.USERS_MANAGE))],
)
async def create_notification(payload: NotificationCreate, db: Session = Depends(get_db)) -> NotificationRead:
    repo = NotificationRepository(db)
    notification = repo.create(payload.model_dump())
    db.commit()
    db.refresh(notification)

    from app.realtime.notifier import publish_notification_created

    await publish_notification_created(notification)

    return NotificationRead.model_validate(notification)


@router.patch("/{notification_id}", response_model=NotificationRead)
def update_notification(
    notification_id: UUID,
    payload: NotificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NotificationRead:
    """Marking a notification read/unread is a personal action — the owner
    can always do this themselves, without needing USERS_MANAGE."""
    repo = NotificationRepository(db)
    notification = repo.get_or_404(notification_id)
    _require_owner_or_permission(notification, current_user, Permission.USERS_MANAGE)

    data = payload.model_dump(exclude_unset=True)
    if data.get("is_read") is True and notification.read_at is None:
        data["read_at"] = datetime.now(timezone.utc)
    elif data.get("is_read") is False:
        data["read_at"] = None

    notification = repo.update(notification, data)
    db.commit()
    db.refresh(notification)
    return NotificationRead.model_validate(notification)


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> None:
    repo = NotificationRepository(db)
    notification = repo.get_or_404(notification_id)
    _require_owner_or_permission(notification, current_user, Permission.USERS_MANAGE)
    repo.delete(notification)
    db.commit()
