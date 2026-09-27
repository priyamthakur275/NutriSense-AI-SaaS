from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.rbac import Permission, require_permission
from app.api.tenant_scope import resolve_institution_scope, verify_object_institution_access
from app.core.rate_limit import RateLimiter
from app.db.session import get_db
from app.models.user import User
from app.repositories.invite import UserInviteRepository
from app.schemas.common import PaginatedResponse, PaginationParams
from app.schemas.invite import InviteAccept, InviteAcceptResponse, InviteCreate, InviteRead
from app.schemas.user import UserPublic
from app.services import invite_service
from app.services.email_service import get_email_service

router = APIRouter(prefix="/invites", tags=["User Invites"])


def _to_public_user(user: User) -> UserPublic:
    return UserPublic(id=user.id, email=user.email, fullName=user.full_name, role=user.role)


@router.get(
    "",
    response_model=PaginatedResponse[InviteRead],
    dependencies=[Depends(require_permission(Permission.USERS_READ))],
)
def list_invites(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    institution_id: UUID | None = Depends(resolve_institution_scope),
) -> PaginatedResponse[InviteRead]:
    repo = UserInviteRepository(db)
    items, total = repo.list(
        pagination=pagination, default_sort_field="created_at", filters={"institution_id": institution_id}
    )
    return PaginatedResponse.build(
        [InviteRead.model_validate(i) for i in items], total_items=total, params=pagination
    )


@router.post(
    "",
    response_model=InviteRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_permission(Permission.USERS_MANAGE)),
        Depends(RateLimiter(times=10, seconds=60, scope="invites_create")),
    ],
)
def create_invite(
    payload: InviteCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> InviteRead:
    verify_object_institution_access(db, current_user, payload.institution_id)
    invite, _raw_token = invite_service.create_invite(
        db, payload, invited_by=current_user, email_service=get_email_service()
    )
    return InviteRead.model_validate(invite)


@router.post(
    "/accept",
    response_model=InviteAcceptResponse,
    dependencies=[Depends(RateLimiter(times=10, seconds=60, scope="invites_accept"))],
)
def accept_invite(payload: InviteAccept, db: Session = Depends(get_db)) -> InviteAcceptResponse:
    """Public — no authentication required. The invitation token itself
    proves the caller is the intended recipient, the same way an email
    verification or password reset token does."""
    user, access_token, refresh_token = invite_service.accept_invite(db, payload)
    return InviteAcceptResponse(access_token=access_token, refresh_token=refresh_token, user=_to_public_user(user))
