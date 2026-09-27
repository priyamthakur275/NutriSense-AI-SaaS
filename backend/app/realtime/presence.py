"""Presence: online/offline/last-seen. Online status is derived directly
from the connection manager (a user with >=1 open connection is online);
last-seen is recorded on disconnect. Presence *changes* are published on
the event bus so any WS client subscribed to the "presence" room gets a
live update without polling — see ws.py's room join handling.
"""

from datetime import datetime

from app.realtime.event_bus import get_event_bus

PRESENCE_ROOM = "presence"


async def publish_presence_change(user_id: str, *, online: bool) -> None:
    from app.realtime.connection_manager import get_connection_manager

    manager = get_connection_manager()
    last_seen = manager.last_seen(user_id)
    await get_event_bus().publish(
        "presence.changed",
        {
            "user_id": user_id,
            "online": online,
            "last_seen": last_seen.isoformat() if last_seen else None,
        },
    )


def get_presence_snapshot(user_id: str) -> dict:
    from app.realtime.connection_manager import get_connection_manager

    manager = get_connection_manager()
    online = manager.is_user_online(user_id)
    last_seen: datetime | None = None if online else manager.last_seen(user_id)
    return {"user_id": user_id, "online": online, "last_seen": last_seen.isoformat() if last_seen else None}
