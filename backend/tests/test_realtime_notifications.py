"""Live notification delivery and presence — event bus wired to the
connection manager, exercised at the handler level (not full WS sockets,
which test_websocket.py already covers for the transport itself)."""

import pytest

from app.realtime.connection_manager import get_connection_manager
from app.realtime.event_bus import get_event_bus
from app.realtime.handlers import register_realtime_handlers
from app.realtime.presence import get_presence_snapshot, publish_presence_change


@pytest.fixture(autouse=True)
def _fresh_handlers():
    """Handlers are normally registered once at app startup; tests running
    in-process need them registered too, and idempotently (registering
    twice would double-deliver)."""
    bus = get_event_bus()
    bus._subscribers.clear()
    register_realtime_handlers()
    yield


@pytest.mark.asyncio
async def test_notification_created_event_delivers_to_online_user(monkeypatch):
    manager = get_connection_manager()
    delivered = []

    async def fake_send_to_user(user_id, message):
        delivered.append((user_id, message))
        return 1

    monkeypatch.setattr(manager, "send_to_user", fake_send_to_user)

    await get_event_bus().publish(
        "notification.created",
        {"id": "abc", "user_id": "user-1", "title": "Test", "message": "hi"},
    )

    assert len(delivered) == 1
    assert delivered[0][0] == "user-1"
    assert delivered[0][1]["type"] == "notification.created"


@pytest.mark.asyncio
async def test_notification_event_with_no_online_connections_is_a_noop(monkeypatch):
    manager = get_connection_manager()

    async def fake_send_to_user(user_id, message):
        return 0  # nobody connected

    monkeypatch.setattr(manager, "send_to_user", fake_send_to_user)

    # Must not raise even though nobody is listening.
    await get_event_bus().publish("notification.created", {"user_id": "offline-user"})


def test_presence_snapshot_reflects_online_state():
    manager = get_connection_manager()
    manager._by_user["online-user"] = {"conn-1"}

    snapshot = get_presence_snapshot("online-user")
    assert snapshot["online"] is True
    assert snapshot["last_seen"] is None

    del manager._by_user["online-user"]
    snapshot = get_presence_snapshot("online-user")
    assert snapshot["online"] is False


@pytest.mark.asyncio
async def test_presence_changed_event_reaches_presence_room(monkeypatch):
    manager = get_connection_manager()
    sent = []

    async def fake_send_to_room(room, message, **kwargs):
        sent.append((room, message))
        return 1

    monkeypatch.setattr(manager, "send_to_room", fake_send_to_room)

    await publish_presence_change("user-2", online=True)

    assert len(sent) == 1
    room, message = sent[0]
    assert room == "presence"
    assert message["type"] == "presence.changed"
    assert message["data"]["user_id"] == "user-2"
    assert message["data"]["online"] is True
