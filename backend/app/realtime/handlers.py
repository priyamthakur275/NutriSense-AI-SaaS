"""Event bus subscribers that bridge domain events to WebSocket delivery.
Registered once at app startup (see app.main). Keeping these as separate
handler functions (rather than publishing directly to the connection
manager from wherever an event originates) is what lets a future
Redis-backed EventBus fan events out across multiple worker processes
without any publisher code changing.
"""

from app.core.logging import get_logger
from app.realtime.connection_manager import get_connection_manager
from app.realtime.event_bus import get_event_bus
from app.realtime.presence import PRESENCE_ROOM

logger = get_logger("app.realtime.handlers")


async def _on_presence_changed(payload: dict) -> None:
    manager = get_connection_manager()
    await manager.send_to_room(PRESENCE_ROOM, {"type": "presence.changed", "data": payload})


async def _on_notification_created(payload: dict) -> None:
    manager = get_connection_manager()
    user_id = payload.get("user_id")
    if not user_id:
        return
    delivered = await manager.send_to_user(user_id, {"type": "notification.created", "data": payload})
    if delivered:
        logger.info("Live-delivered notification to user=%s (%d connection(s))", user_id, delivered)


def register_realtime_handlers() -> None:
    bus = get_event_bus()
    bus.subscribe("presence.changed", _on_presence_changed)
    bus.subscribe("notification.created", _on_notification_created)
    logger.info("Realtime event handlers registered")
