"""In-process async pub/sub. Same honest caveat as app.core.rate_limit /
app.agents.utils.cache: correct for a single-process deployment only. The
`EventBus` interface is the swap point for a Redis Pub/Sub or NATS-backed
implementation once running more than one worker — every publisher/
subscriber depends on `get_event_bus()`, never this module's internals.
"""

import asyncio
from collections import defaultdict
from collections.abc import Awaitable, Callable
from typing import Any

from app.core.logging import get_logger

logger = get_logger("app.realtime.event_bus")

EventHandler = Callable[[dict[str, Any]], Awaitable[None]]


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        handlers = self._subscribers.get(event_type)
        if handlers and handler in handlers:
            handlers.remove(handler)

    async def publish(self, event_type: str, payload: dict[str, Any]) -> None:
        """Dispatches to every subscriber concurrently. A handler raising
        never blocks/breaks the others, or the publisher — this is
        fire-and-forget event delivery, not a synchronous call chain."""
        handlers = list(self._subscribers.get(event_type, ()))
        if not handlers:
            return

        results = await asyncio.gather(
            *(self._run_handler(h, event_type, payload) for h in handlers), return_exceptions=True
        )
        for result in results:
            if isinstance(result, Exception):
                logger.exception("Event handler failed for '%s'", event_type, exc_info=result)

    async def _run_handler(self, handler: EventHandler, event_type: str, payload: dict[str, Any]) -> None:
        await handler(payload)


_bus = EventBus()


def get_event_bus() -> EventBus:
    return _bus
