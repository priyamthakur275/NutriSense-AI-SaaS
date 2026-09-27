"""Audit middleware regression tests: proves mutations and access-denials
are logged automatically, with zero per-endpoint instrumentation."""

from starlette.testclient import TestClient

from app.main import app


def _register_and_login(client: TestClient, email: str) -> tuple[str, str]:
    resp = client.post(
        "/api/v1/auth/register",
        json={"full_name": "Audit Test", "email": email, "password": "AuditPass123"},
    )
    body = resp.json()
    return body["access_token"], body["user"]["id"]


def test_successful_mutation_is_audit_logged():
    client = TestClient(app)
    token, user_id = _register_and_login(client, "audit1@test.com")

    resp = client.patch(
        "/api/v1/nutrition-profile/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"age": 30},
    )
    assert resp.status_code == 200

    from app.db.session import SessionLocal
    from app.models.audit_log import AuditLog

    db = SessionLocal()
    try:
        entry = (
            db.query(AuditLog)
            .filter(AuditLog.user_id == user_id, AuditLog.entity_type == "nutrition-profile")
            .first()
        )
        assert entry is not None
        assert entry.action.value == "update"
        assert entry.details["status_code"] == 200
    finally:
        db.close()


def test_access_denial_is_audit_logged():
    client = TestClient(app)
    token, user_id = _register_and_login(client, "audit2@test.com")

    # A freshly registered user is a STUDENT — creating an institution
    # requires SUPER_ADMIN, so this must be denied.
    resp = client.post(
        "/api/v1/institutions",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Should Be Denied", "type": "school"},
    )
    assert resp.status_code == 403

    from app.db.session import SessionLocal
    from app.models.audit_log import AuditLog

    db = SessionLocal()
    try:
        entry = (
            db.query(AuditLog)
            .filter(AuditLog.user_id == user_id, AuditLog.action == "access_denied")
            .first()
        )
        assert entry is not None
        assert entry.entity_type == "institutions"
        assert entry.details["status_code"] == 403
    finally:
        db.close()


def test_get_requests_are_not_logged_as_mutations():
    """GET is read-only — it should never produce a create/update/delete
    audit entry (a 401/403 GET is still logged as access_denied, but a
    *successful* GET is deliberately not noise in the audit trail)."""
    client = TestClient(app)
    token, user_id = _register_and_login(client, "audit3@test.com")

    resp = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200

    from app.db.session import SessionLocal
    from app.models.audit_log import AuditLog

    db = SessionLocal()
    try:
        entries = db.query(AuditLog).filter(AuditLog.user_id == user_id, AuditLog.entity_type == "users").all()
        assert entries == []
    finally:
        db.close()


def test_login_is_not_double_logged_by_middleware():
    """auth_service already writes a richer LOGIN entry — the middleware
    must not also write a generic 'create' entry for POST /auth/login."""
    client = TestClient(app)
    token, user_id = _register_and_login(client, "audit4@test.com")

    client.post("/api/v1/auth/login", json={"email": "audit4@test.com", "password": "AuditPass123"})

    from app.db.session import SessionLocal
    from app.models.audit_log import AuditLog

    db = SessionLocal()
    try:
        login_entries = db.query(AuditLog).filter(AuditLog.user_id == user_id, AuditLog.action == "login").all()
        generic_auth_entries = (
            db.query(AuditLog).filter(AuditLog.user_id == user_id, AuditLog.entity_type == "auth").all()
        )
        assert len(login_entries) == 1  # from auth_service, the specific entry
        assert generic_auth_entries == []  # middleware correctly excluded /auth/*
    finally:
        db.close()
