from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.rbac import Permission, require_permission
from app.core.exceptions import DuplicateResourceError
from app.core.security import hash_password
from app.db.session import get_db
from app.models.enums import AuditAction
from app.models.audit_log import AuditLog
from app.models.user import User, UserRole
from app.repositories.user import UserRepository
from app.schemas.common import PaginatedResponse, PaginationParams, SortParams
from app.schemas.user import BulkOperationResult, BulkUserIds, UserAdminCreate, UserAdminUpdate, UserRead

router = APIRouter(prefix="/users", tags=["Users"])

_SORTABLE_FIELDS = {"full_name", "email", "role", "created_at"}


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get(
    "",
    response_model=PaginatedResponse[UserRead],
    dependencies=[Depends(require_permission(Permission.USERS_READ))],
)
def list_users(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    sort: SortParams = Depends(),
    search: str | None = Query(None, description="Search by name or email"),
    role: UserRole | None = Query(None, description="Filter by role"),
    is_active: bool | None = Query(None, description="Filter by active status"),
) -> PaginatedResponse[UserRead]:
    repo = UserRepository(db)
    items, total = repo.list(
        pagination=pagination,
        sort=sort,
        allowed_sort_fields=_SORTABLE_FIELDS,
        search=search,
        search_fields=["full_name", "email"] if search else None,
        filters={"role": role, "is_active": is_active},
    )
    return PaginatedResponse.build(
        [UserRead.model_validate(u) for u in items], total_items=total, params=pagination
    )


@router.get(
    "/{user_id}",
    response_model=UserRead,
    dependencies=[Depends(require_permission(Permission.USERS_READ))],
)
def get_user(user_id: str, db: Session = Depends(get_db)) -> UserRead:
    repo = UserRepository(db)
    return UserRead.model_validate(repo.get_or_404(user_id))


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(Permission.USERS_MANAGE))],
)
def create_user(
    payload: UserAdminCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> UserRead:
    repo = UserRepository(db)
    data = payload.model_dump(exclude={"password"})
    data["hashed_password"] = hash_password(payload.password)
    try:
        user = repo.create(data)
        db.add(AuditLog(user_id=current_user.id, action=AuditAction.CREATE, entity_type="User", entity_id=user.id))
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateResourceError(f"Email '{payload.email}' is already registered") from exc
    db.refresh(user)
    return UserRead.model_validate(user)


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    dependencies=[Depends(require_permission(Permission.USERS_MANAGE))],
)
def update_user(
    user_id: str,
    payload: UserAdminUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserRead:
    repo = UserRepository(db)
    user = repo.get_or_404(user_id)
    user = repo.update(user, payload.model_dump(exclude_unset=True))
    db.add(
        AuditLog(user_id=current_user.id, action=AuditAction.UPDATE, entity_type="User", entity_id=user.id)
    )
    db.commit()
    db.refresh(user)
    return UserRead.model_validate(user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission(Permission.USERS_MANAGE))],
)
def delete_user(
    user_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> None:
    """Soft-delete only. `User.deleted_at` is checked by `get_current_user`
    (Phase 4C), so a soft-deleted user's existing access token stops
    working immediately, without needing separate revocation logic here."""
    repo = UserRepository(db)
    user = repo.get_or_404(user_id)
    repo.delete(user)
    db.add(
        AuditLog(user_id=current_user.id, action=AuditAction.DELETE, entity_type="User", entity_id=user.id)
    )
    db.commit()


@router.post(
    "/{user_id}/restore",
    response_model=UserRead,
    dependencies=[Depends(require_permission(Permission.USERS_MANAGE))],
)
def restore_user(
    user_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> UserRead:
    """Reverses a soft-delete — e.g. an account deactivated by mistake, or
    a returning student/staff member. The account's access token was
    invalidated at delete time (get_current_user rejects deleted_at IS NOT
    NULL); restoring clears that, but the user still needs to log in again
    to obtain a fresh token — restoring doesn't retroactively resurrect
    their old session."""
    repo = UserRepository(db)
    user = repo.get_deleted_or_404(user_id)
    user = repo.restore(user)
    db.add(
        AuditLog(user_id=current_user.id, action=AuditAction.UPDATE, entity_type="User", entity_id=user.id, details={"restored": True})
    )
    db.commit()
    db.refresh(user)
    return UserRead.model_validate(user)


@router.post(
    "/bulk-deactivate",
    response_model=BulkOperationResult,
    dependencies=[Depends(require_permission(Permission.USERS_MANAGE))],
)
def bulk_deactivate_users(
    payload: BulkUserIds, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> BulkOperationResult:
    repo = UserRepository(db)
    succeeded, failed = [], []
    for uid in payload.user_ids:
        user = repo.get(uid)
        if user is None:
            failed.append(uid)
            continue
        repo.delete(user)
        db.add(AuditLog(user_id=current_user.id, action=AuditAction.DELETE, entity_type="User", entity_id=uid, details={"bulk": True}))
        succeeded.append(uid)
    db.commit()
    return BulkOperationResult(succeeded=succeeded, failed=failed)


@router.post(
    "/bulk-restore",
    response_model=BulkOperationResult,
    dependencies=[Depends(require_permission(Permission.USERS_MANAGE))],
)
def bulk_restore_users(
    payload: BulkUserIds, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> BulkOperationResult:
    repo = UserRepository(db)
    succeeded, failed = [], []
    for uid in payload.user_ids:
        try:
            user = repo.get_deleted_or_404(uid)
        except Exception:
            failed.append(uid)
            continue
        repo.restore(user)
        db.add(AuditLog(user_id=current_user.id, action=AuditAction.UPDATE, entity_type="User", entity_id=uid, details={"bulk_restore": True}))
        succeeded.append(uid)
    db.commit()
    return BulkOperationResult(succeeded=succeeded, failed=failed)
