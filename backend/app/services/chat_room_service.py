"""ChatRoom membership + message persistence. WS handlers (ws.py) and REST
endpoints (chat_rooms.py) both call into this — single source of truth for
what counts as a valid send/read.
"""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import AuthorizationError, NotFoundError
from app.models.chat_room import ChatRoom
from app.models.chat_room_member import ChatRoomMember
from app.models.enums import ChatRoomType
from app.models.room_message import RoomMessage
from app.models.user import User


def is_member(db: Session, room_id: UUID, user_id: str) -> bool:
    return (
        db.query(ChatRoomMember)
        .filter(ChatRoomMember.room_id == room_id, ChatRoomMember.user_id == user_id)
        .first()
        is not None
    )


def get_or_create_direct_room(db: Session, *, institution_id: UUID, user_a: User, user_b_id: str) -> ChatRoom:
    """Finds an existing DIRECT room between exactly these two users, or
    creates one. Prevents duplicate DM threads for the same pair."""
    existing = (
        db.query(ChatRoom)
        .join(ChatRoomMember, ChatRoomMember.room_id == ChatRoom.id)
        .filter(ChatRoom.institution_id == institution_id, ChatRoom.type == ChatRoomType.DIRECT)
        .filter(ChatRoomMember.user_id.in_([user_a.id, user_b_id]))
        .all()
    )
    for room in existing:
        member_ids = {m.user_id for m in room.members}
        if member_ids == {user_a.id, user_b_id}:
            return room

    return create_room(
        db, institution_id=institution_id, type_=ChatRoomType.DIRECT, name=None,
        member_ids=[user_b_id], created_by=user_a,
    )


def create_room(db: Session, *, institution_id: UUID, type_: ChatRoomType, name: str | None, member_ids: list[str], created_by: User) -> ChatRoom:
    room = ChatRoom(institution_id=institution_id, type=type_, name=name, created_by_id=created_by.id)
    db.add(room)
    db.flush()

    all_members = set(member_ids) | {created_by.id}
    for uid in all_members:
        db.add(ChatRoomMember(room_id=room.id, user_id=uid))
    db.commit()
    db.refresh(room)
    return room


def send_message(db: Session, *, room_id: UUID, sender: User, content: str) -> RoomMessage:
    if not is_member(db, room_id, sender.id):
        raise AuthorizationError("You are not a member of this chat room")
    message = RoomMessage(room_id=room_id, sender_id=sender.id, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def mark_read(db: Session, *, room_id: UUID, user_id: str) -> None:
    member = (
        db.query(ChatRoomMember)
        .filter(ChatRoomMember.room_id == room_id, ChatRoomMember.user_id == user_id)
        .first()
    )
    if member is None:
        raise AuthorizationError("You are not a member of this chat room")
    member.last_read_at = datetime.now(timezone.utc)
    db.commit()


def get_room_or_404(db: Session, room_id: UUID) -> ChatRoom:
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
    if room is None:
        raise NotFoundError(f"Chat room '{room_id}' not found")
    return room
