from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.tenant_scope import verify_object_institution_access
from app.core.exceptions import AuthorizationError
from app.db.session import get_db
from app.models.user import User
from app.repositories.room_message import RoomMessageRepository
from app.schemas.chat_room import ChatRoomCreate, ChatRoomRead, DirectRoomRequest, RoomMessageRead
from app.schemas.common import PaginatedResponse, PaginationParams
from app.services import chat_room_service

router = APIRouter(prefix="/chat-rooms", tags=["Chat Rooms"])


@router.post("", response_model=ChatRoomRead, status_code=status.HTTP_201_CREATED)
def create_room(payload: ChatRoomCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> ChatRoomRead:
    verify_object_institution_access(db, current_user, payload.institution_id)
    room = chat_room_service.create_room(
        db, institution_id=payload.institution_id, type_=payload.type, name=payload.name,
        member_ids=payload.member_ids, created_by=current_user,
    )
    return ChatRoomRead.model_validate(room)


@router.post("/direct", response_model=ChatRoomRead)
def get_or_create_direct(payload: DirectRoomRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> ChatRoomRead:
    verify_object_institution_access(db, current_user, payload.institution_id)
    room = chat_room_service.get_or_create_direct_room(db, institution_id=payload.institution_id, user_a=current_user, user_b_id=payload.other_user_id)
    return ChatRoomRead.model_validate(room)


@router.get("/{room_id}/messages", response_model=PaginatedResponse[RoomMessageRead])
def list_messages(room_id: UUID, db: Session = Depends(get_db), pagination: PaginationParams = Depends(), current_user: User = Depends(get_current_user)) -> PaginatedResponse[RoomMessageRead]:
    """Reconnection / missed-event recovery path: a client that was
    offline fetches everything it missed via this paginated history —
    messages are never lost, only delivered late."""
    if not chat_room_service.is_member(db, room_id, current_user.id):
        raise AuthorizationError("You are not a member of this chat room")
    repo = RoomMessageRepository(db)
    items, total = repo.list(pagination=pagination, default_sort_field="created_at", filters={"room_id": room_id})
    return PaginatedResponse.build([RoomMessageRead.model_validate(m) for m in items], total_items=total, params=pagination)


@router.post("/{room_id}/read", status_code=status.HTTP_204_NO_CONTENT)
def mark_read(room_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> None:
    chat_room_service.mark_read(db, room_id=room_id, user_id=current_user.id)
