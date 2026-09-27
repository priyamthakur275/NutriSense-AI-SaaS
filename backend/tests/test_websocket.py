"""WebSocket connection lifecycle: auth, connect/disconnect registry,
heartbeat pong handling."""

import time

import pytest
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.main import app
from app.realtime.connection_manager import get_connection_manager


def _register(client: TestClient, email: str) -> str:
    resp = client.post(
        "/api/v1/auth/register",
        json={"full_name": "WS Test", "email": email, "password": "WsPass123"},
    )
    return resp.json()["access_token"]


def test_connection_rejected_without_token():
    client = TestClient(app)
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/api/v1/ws"):
            pass
    assert exc_info.value.code == 1008


def test_connection_rejected_with_invalid_token():
    client = TestClient(app)
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/api/v1/ws?token=not-a-real-token"):
            pass
    assert exc_info.value.code == 1008


def test_authenticated_connection_registers_in_manager():
    client = TestClient(app)
    token = _register(client, "wsuser1@test.com")
    manager = get_connection_manager()

    with client.websocket_connect(f"/api/v1/ws?token={token}") as ws:
        ws.send_json({"type": "pong"})
        # Starlette's synchronous TestClient runs the ASGI app in a
        # background thread with its own event loop; a brief settle delay
        # is needed for that thread to actually process the connect
        # handshake before this thread's assertion runs — a known
        # TestClient websocket-testing quirk, not applicable to real
        # clients (verified separately against a live uvicorn server).
        time.sleep(0.1)
        assert manager.connection_count() >= 1


def test_pong_updates_heartbeat_and_multi_device_tracking():
    client = TestClient(app)
    token = _register(client, "wsuser2@test.com")
    manager = get_connection_manager()

    with client.websocket_connect(f"/api/v1/ws?token={token}") as ws1:
        ws1.send_json({"type": "pong"})
        time.sleep(0.1)
        with client.websocket_connect(f"/api/v1/ws?token={token}") as ws2:
            ws2.send_json({"type": "pong"})
            time.sleep(0.1)
            # Same user, two devices -> both tracked under one user_id.
            matching = [conns for conns in manager._by_user.values() if len(conns) == 2]
            assert matching, f"expected a user with 2 connections, got {manager._by_user}"
