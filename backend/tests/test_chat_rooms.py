"""Chat room service: membership authorization, message persistence,
read-receipt tracking."""

import pytest

from app.core.exceptions import AuthorizationError
from app.models.enums import ChatRoomType
from app.services import chat_room_service


def test_non_member_cannot_send_message(db_session, make_user, make_institution):
    institution = make_institution()
    owner = make_user()
    outsider = make_user()

    room = chat_room_service.create_room(
        db_session, institution_id=institution.id, type_=ChatRoomType.DIRECT, name=None,
        member_ids=[], created_by=owner,
    )

    with pytest.raises(AuthorizationError):
        chat_room_service.send_message(db_session, room_id=room.id, sender=outsider, content="hi")


def test_member_can_send_and_message_persists(db_session, make_user, make_institution):
    institution = make_institution()
    owner = make_user()

    room = chat_room_service.create_room(
        db_session, institution_id=institution.id, type_=ChatRoomType.GROUP, name="Team",
        member_ids=[], created_by=owner,
    )
    message = chat_room_service.send_message(db_session, room_id=room.id, sender=owner, content="hello")

    assert message.room_id == room.id
    assert message.content == "hello"


def test_mark_read_rejected_for_non_member(db_session, make_user, make_institution):
    institution = make_institution()
    owner = make_user()
    outsider = make_user()
    room = chat_room_service.create_room(
        db_session, institution_id=institution.id, type_=ChatRoomType.DIRECT, name=None,
        member_ids=[], created_by=owner,
    )

    with pytest.raises(AuthorizationError):
        chat_room_service.mark_read(db_session, room_id=room.id, user_id=outsider.id)


def test_is_member_reflects_creation(db_session, make_user, make_institution):
    institution = make_institution()
    owner = make_user()
    member = make_user()
    room = chat_room_service.create_room(
        db_session, institution_id=institution.id, type_=ChatRoomType.GROUP, name=None,
        member_ids=[member.id], created_by=owner,
    )
    assert chat_room_service.is_member(db_session, room.id, owner.id)
    assert chat_room_service.is_member(db_session, room.id, member.id)


def test_get_or_create_direct_room_is_idempotent(db_session, make_user, make_institution):
    institution = make_institution()
    a = make_user()
    b = make_user()

    r1 = chat_room_service.get_or_create_direct_room(db_session, institution_id=institution.id, user_a=a, user_b_id=b.id)
    r2 = chat_room_service.get_or_create_direct_room(db_session, institution_id=institution.id, user_a=a, user_b_id=b.id)

    assert r1.id == r2.id
