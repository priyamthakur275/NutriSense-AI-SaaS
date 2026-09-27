"""WebSocket authentication. Browsers' native WebSocket API cannot set an
Authorization header on the handshake request, so the access token is
passed as a query parameter (`wss://host/ws?token=...`) — the standard
approach. Everything past that point reuses the exact same validation
app.api.deps.get_current_user applies to normal HTTP requests (same
decode function, same active/locked/deleted checks), so a token that's
rejected for REST is rejected here too, and vice versa.
"""

from fastapi import WebSocket, status
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.models.user import User


class WebSocketAuthError(Exception):
    def __init__(self, code: int, reason: str) -> None:
        self.code = code
        self.reason = reason
        super().__init__(reason)


async def authenticate_websocket(websocket: WebSocket, db: Session) -> User:
    token = websocket.query_params.get("token")
    if not token:
        raise WebSocketAuthError(status.WS_1008_POLICY_VIOLATION, "Missing token")

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise WebSocketAuthError(status.WS_1008_POLICY_VIOLATION, "Invalid or expired token")

    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user or not user.is_active or user.deleted_at is not None:
        raise WebSocketAuthError(status.WS_1008_POLICY_VIOLATION, "Account unavailable")

    if user.is_locked:
        raise WebSocketAuthError(status.WS_1008_POLICY_VIOLATION, "Account is temporarily locked")

    return user
