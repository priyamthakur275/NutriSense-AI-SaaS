"""Publishes a "notification.created" event for a just-persisted
Notification row. Called from wherever a Notification is created
(notifications.py's create endpoint, announcement_service's fan-out) —
those call sites still own persistence via the existing
NotificationRepository; this only adds the live-delivery side effect.
"""

from app.models.notification import Notification
from app.realtime.event_bus import get_event_bus


async def publish_notification_created(notification: Notification) -> None:
    await get_event_bus().publish(
        "notification.created",
        {
            "id": str(notification.id),
            "user_id": notification.user_id,
            "type": notification.type.value,
            "title": notification.title,
            "message": notification.message,
            "is_read": notification.is_read,
            "created_at": notification.created_at.isoformat(),
        },
    )
