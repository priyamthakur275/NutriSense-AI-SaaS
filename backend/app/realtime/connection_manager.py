"""WebSocket connection registry: user_id -> {device connections}, plus
room membership for institution/broadcast/chat-room delivery. Multi-device
by design — a user open on two tabs/devices gets both connections tracked
independently under the same user_id, and both receive every message
addressed to that user.
"""

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from fastapi import WebSocket

from app.core.logging import get_logger

logger = get_logger("app.realtime.connections")


@dataclass
class ConnectionInfo:
    connection_id: str
    user_id: str
    websocket: WebSocket
    rooms: set[str] = field(default_factory=set)
    connected_at: float = field(default_factory=time.monotonic)
    last_pong_at: float = field(default_factory=time.monotonic)


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[str, ConnectionInfo] = {}
        self._by_user: dict[str, set[str]] = {}
        self._by_room: dict[str, set[str]] = {}
        # Survives a user going offline — updated on every disconnect, read
        # by the presence endpoint/event for "last seen" when the user
        # isn't currently online. Not persisted to the DB: an in-memory
        # approximation is sufficient for presence (unlike audit/financial
        # data, losing this on a process restart is an acceptable
        # trade-off, and avoids a DB write on every disconnect).
        self._last_seen: dict[str, datetime] = {}

    async def connect(self, websocket: WebSocket, user_id: str) -> ConnectionInfo:
        await websocket.accept()
        connection_id = str(uuid.uuid4())
        info = ConnectionInfo(connection_id=connection_id, user_id=user_id, websocket=websocket)
        was_offline = user_id not in self._by_user
        self._connections[connection_id] = info
        self._by_user.setdefault(user_id, set()).add(connection_id)
        logger.info("WS connected user=%s connection=%s (device count=%d)", user_id, connection_id, len(self._by_user[user_id]))

        if was_offline:
            from app.realtime.presence import publish_presence_change

            await publish_presence_change(user_id, online=True)

        return info

    def disconnect(self, connection_id: str) -> None:
        info = self._connections.pop(connection_id, None)
        if info is None:
            return
        user_conns = self._by_user.get(info.user_id)
        went_offline = False
        if user_conns:
            user_conns.discard(connection_id)
            if not user_conns:
                del self._by_user[info.user_id]
                went_offline = True
        for room in list(info.rooms):
            room_members = self._by_room.get(room)
            if room_members:
                room_members.discard(connection_id)
                if not room_members:
                    del self._by_room[room]
        logger.info("WS disconnected user=%s connection=%s", info.user_id, connection_id)

        if went_offline:
            self._last_seen[info.user_id] = datetime.now(timezone.utc)
            import asyncio

            from app.realtime.presence import publish_presence_change

            asyncio.create_task(publish_presence_change(info.user_id, online=False))

    def last_seen(self, user_id: str) -> datetime | None:
        return self._last_seen.get(user_id)

    def join_room(self, connection_id: str, room: str) -> None:
        info = self._connections.get(connection_id)
        if info is None:
            return
        info.rooms.add(room)
        self._by_room.setdefault(room, set()).add(connection_id)

    def leave_room(self, connection_id: str, room: str) -> None:
        info = self._connections.get(connection_id)
        if info is not None:
            info.rooms.discard(room)
        members = self._by_room.get(room)
        if members:
            members.discard(connection_id)
            if not members:
                del self._by_room[room]

    def is_user_online(self, user_id: str) -> bool:
        return bool(self._by_user.get(user_id))

    def online_user_ids(self) -> set[str]:
        return set(self._by_user.keys())

    def connection_count(self) -> int:
        return len(self._connections)

    def mark_pong(self, connection_id: str) -> None:
        info = self._connections.get(connection_id)
        if info is not None:
            info.last_pong_at = time.monotonic()

    def stale_connection_ids(self, *, timeout_seconds: float) -> list[str]:
        """Connections that haven't ponged within the heartbeat timeout —
        candidates for the server to forcibly close (a dead TCP connection
        the client never cleanly closed)."""
        now = time.monotonic()
        return [cid for cid, info in self._connections.items() if now - info.last_pong_at > timeout_seconds]

    async def send_to_connection(self, connection_id: str, message: dict) -> bool:
        info = self._connections.get(connection_id)
        if info is None:
            return False
        try:
            await info.websocket.send_json(message)
            return True
        except Exception:
            logger.warning("Failed to send to connection=%s, disconnecting it", connection_id)
            self.disconnect(connection_id)
            return False

    async def send_to_user(self, user_id: str, message: dict) -> int:
        """Delivers to every device the user has connected. Returns the
        number of connections the message was actually sent to."""
        connection_ids = list(self._by_user.get(user_id, ()))
        sent = 0
        for cid in connection_ids:
            if await self.send_to_connection(cid, message):
                sent += 1
        return sent

    async def send_to_room(self, room: str, message: dict, *, exclude_connection_id: str | None = None) -> int:
        connection_ids = [cid for cid in self._by_room.get(room, ()) if cid != exclude_connection_id]
        sent = 0
        for cid in connection_ids:
            if await self.send_to_connection(cid, message):
                sent += 1
        return sent

    async def broadcast(self, message: dict) -> int:
        connection_ids = list(self._connections.keys())
        sent = 0
        for cid in connection_ids:
            if await self.send_to_connection(cid, message):
                sent += 1
        return sent


_manager = ConnectionManager()


def get_connection_manager() -> ConnectionManager:
    return _manager
