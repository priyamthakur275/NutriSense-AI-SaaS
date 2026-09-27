"""WebSocket entrypoint: authenticate, register with the connection
manager, run a heartbeat, and dispatch inbound client messages. Message
handling for specific event types (chat, typing, notifications ack) is
added in later chunks — this chunk establishes the connection lifecycle
every one of those will run on top of.
"""

import asyncio

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from starlette.websockets import WebSocketState

from app.core.logging import get_logger
from app.db.session import get_db
from app.realtime.auth import WebSocketAuthError, authenticate_websocket
from app.realtime.connection_manager import ConnectionManager, get_connection_manager

router = APIRouter(tags=["Realtime"])
logger = get_logger("app.realtime.ws")

HEARTBEAT_INTERVAL_SECONDS = 20
HEARTBEAT_TIMEOUT_SECONDS = 45


def _room_key(room_id) -> str:
    return f"chat:{room_id}"


def _can_join_chat_room(db: Session, room: str, user_id: str) -> bool:
    from uuid import UUID

    from app.services.chat_room_service import is_member

    try:
        room_id = UUID(room.removeprefix("chat:"))
    except ValueError:
        return False
    return is_member(db, room_id, user_id)


async def _handle_room_message(db: Session, manager: ConnectionManager, connection_id: str, user, data: dict) -> None:
    from uuid import UUID

    from app.core.exceptions import AppError
    from app.services.chat_room_service import send_message

    raw_room_id = data.get("room_id")
    content = data.get("content")
    if not raw_room_id or not isinstance(content, str) or not content.strip():
        await manager.send_to_connection(connection_id, {"type": "error", "message": "room_id and content required"})
        return

    try:
        room_id = UUID(raw_room_id)
        message = send_message(db, room_id=room_id, sender=user, content=content)
    except AppError as exc:
        await manager.send_to_connection(connection_id, {"type": "error", "message": exc.message})
        return

    payload = {
        "type": "room_message",
        "data": {
            "id": str(message.id),
            "room_id": str(message.room_id),
            "sender_id": message.sender_id,
            "content": message.content,
            "created_at": message.created_at.isoformat(),
        },
    }
    # The sender is always a room member (send_message would have raised
    # AuthorizationError otherwise), so this single broadcast is also the
    # sender's own delivery confirmation — the persisted message.id in the
    # payload they receive back is what a client reconciles an
    # optimistically-rendered local message against. No separate ack
    # message is sent; that would just double-deliver to the sender.
    await manager.send_to_room(_room_key(room_id), payload)


async def _handle_typing(manager: ConnectionManager, connection_id: str, user, data: dict) -> None:
    room_id = data.get("room_id")
    if not room_id:
        return
    await manager.send_to_room(
        _room_key(room_id),
        {"type": "typing", "data": {"room_id": room_id, "user_id": user.id, "is_typing": bool(data.get("is_typing", True))}},
        exclude_connection_id=connection_id,
    )


async def _handle_read_receipt(db: Session, manager: ConnectionManager, user, data: dict) -> None:
    from uuid import UUID

    from app.core.exceptions import AppError
    from app.services.chat_room_service import mark_read

    raw_room_id = data.get("room_id")
    if not raw_room_id:
        return
    try:
        room_id = UUID(raw_room_id)
        mark_read(db, room_id=room_id, user_id=user.id)
    except AppError:
        return
    await manager.send_to_room(_room_key(room_id), {"type": "read_receipt", "data": {"room_id": raw_room_id, "user_id": user.id}})


async def _heartbeat_loop(manager: ConnectionManager, connection_id: str) -> None:
    try:
        while True:
            await asyncio.sleep(HEARTBEAT_INTERVAL_SECONDS)
            delivered = await manager.send_to_connection(connection_id, {"type": "ping"})
            if not delivered:
                return
            if connection_id in manager.stale_connection_ids(timeout_seconds=HEARTBEAT_TIMEOUT_SECONDS):
                logger.info("Closing stale connection=%s (missed heartbeat)", connection_id)
                manager.disconnect(connection_id)
                return
    except asyncio.CancelledError:
        return


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)) -> None:
    try:
        user = await authenticate_websocket(websocket, db)
    except WebSocketAuthError as exc:
        await websocket.close(code=exc.code, reason=exc.reason)
        return

    manager = get_connection_manager()
    connection = await manager.connect(websocket, user.id)
    heartbeat_task = asyncio.create_task(_heartbeat_loop(manager, connection.connection_id))

    try:
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")

            if message_type == "pong":
                manager.mark_pong(connection.connection_id)
            elif message_type == "join_room":
                room = data.get("room")
                if isinstance(room, str) and room:
                    if room.startswith("chat:") and not _can_join_chat_room(db, room, user.id):
                        await websocket.send_json({"type": "error", "message": "Not a member of this room"})
                    else:
                        manager.join_room(connection.connection_id, room)
                        await websocket.send_json({"type": "room_joined", "room": room})
            elif message_type == "leave_room":
                room = data.get("room")
                if isinstance(room, str) and room:
                    manager.leave_room(connection.connection_id, room)
                    await websocket.send_json({"type": "room_left", "room": room})
            elif message_type == "room_message":
                await _handle_room_message(db, manager, connection.connection_id, user, data)
            elif message_type == "typing":
                await _handle_typing(manager, connection.connection_id, user, data)
            elif message_type == "read_receipt":
                await _handle_read_receipt(db, manager, user, data)
            else:
                logger.debug(
                    "Unhandled WS message type=%s from user=%s (no handler registered yet)",
                    message_type,
                    user.id,
                )
    except WebSocketDisconnect:
        pass
    except Exception:
        logger.exception("WS connection error for user=%s", user.id)
    finally:
        heartbeat_task.cancel()
        manager.disconnect(connection.connection_id)
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close()
