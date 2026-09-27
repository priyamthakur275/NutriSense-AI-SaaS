"""Shared pytest fixtures for the integration test suite.

Two distinct testing strategies are used, deliberately kept separate:

  1. `db_session` — an isolated in-memory SQLite engine per test, used by
     tests that call service/engine functions directly (app.agents.*,
     app.services.*). Fast, fully isolated, no relation to the app's real
     engine.

  2. Tests using `starlette.testclient.TestClient(app)` (see
     test_audit_middleware.py) exercise the *real* app, including
     middleware — which means they go through `app.db.session.engine`,
     the same module-level engine every request handler and the
     AuditMiddleware use via `get_db()` / `SessionLocal()` directly. That
     engine is created once, at import time, from `settings.DATABASE_URL`.
     The `DATABASE_URL` env var is therefore set here to a shared temp
     SQLite *file* (not `:memory:` — an in-memory DB is connection-scoped,
     and the app's engine uses NullPool, handing out a fresh connection
     per checkout, so `:memory:` would silently give every request an
     empty, disconnected database) — and this must happen before
     `app.db.session` (or anything importing it) is ever imported,
     otherwise the engine would already be bound to whatever
     `DATABASE_URL` the environment happened to have (typically the
     unreachable Postgres default).
"""

import os
import tempfile

_TEST_DB_FD, _TEST_DB_PATH = tempfile.mkstemp(suffix=".db")
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB_PATH}"
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production-use-only")

import pytest  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.db.session import Base, engine as app_engine  # noqa: E402
from app import models  # noqa: F401,E402  registers all models with Base.metadata

# Create every table once, in the shared temp file, for TestClient-based
# tests that exercise the real app end-to-end.
Base.metadata.create_all(app_engine)


@pytest.fixture()
def db_session():
    """Isolated in-memory engine — unrelated to the app's real engine
    above. Used by tests that call service functions directly."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def make_institution(db_session):
    from app.models.institution import Institution
    from app.models.enums import InstitutionType

    def _make(name="Test Institution"):
        inst = Institution(name=name, type=InstitutionType.SCHOOL)
        db_session.add(inst)
        db_session.flush()
        return inst

    return _make


@pytest.fixture()
def make_user(db_session):
    from app.models.user import User, UserRole
    from app.core.security import hash_password

    counter = {"n": 0}

    def _make(role=UserRole.STUDENT):
        counter["n"] += 1
        user = User(
            full_name=f"Test User {counter['n']}",
            email=f"testuser{counter['n']}@example.com",
            hashed_password=hash_password("TestPass123"),
            role=role,
        )
        db_session.add(user)
        db_session.flush()
        return user

    return _make


@pytest.fixture()
def make_student(db_session):
    from app.models.student import Student

    counter = {"n": 0}

    def _make(user, institution):
        counter["n"] += 1
        student = Student(
            user_id=user.id, institution_id=institution.id, enrollment_number=f"ENR-{counter['n']:04d}"
        )
        db_session.add(student)
        db_session.flush()
        return student

    return _make


@pytest.fixture()
def make_meal(db_session):
    from app.models.meal import Meal
    from app.models.enums import MealType, MealStatus
    from datetime import datetime, timezone

    def _make(institution, served_at=None, status=MealStatus.ANALYZED):
        meal = Meal(
            institution_id=institution.id,
            name="Test Meal",
            meal_type=MealType.LUNCH,
            status=status,
            served_at=served_at or datetime.now(timezone.utc),
        )
        db_session.add(meal)
        db_session.flush()
        return meal

    return _make


@pytest.fixture(autouse=True)
def reset_ai_provider_settings():
    """Every AI test monkeypatches AI_PROVIDER/AI_FALLBACK_PROVIDERS onto a
    stub — this fixture restores the real defaults afterward so no test
    can leak its stub configuration into a later, unrelated test."""
    from app.core.config import settings

    original_provider = settings.AI_PROVIDER
    original_fallbacks = list(settings.AI_FALLBACK_PROVIDERS)
    original_retries = settings.AI_MAX_RETRIES
    yield
    settings.AI_PROVIDER = original_provider
    settings.AI_FALLBACK_PROVIDERS = original_fallbacks
    settings.AI_MAX_RETRIES = original_retries


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """The rate limiter (app.core.rate_limit) tracks hits per client IP in
    module-level process memory. Every TestClient-based test appears to
    come from the same synthetic "testclient" IP, so without resetting
    this between tests, the 4th test in a file that each call
    `/auth/register` once would spuriously hit the 3-per-minute limit and
    fail with a 429 that has nothing to do with what that test is
    actually verifying."""
    from app.core.rate_limit import InMemoryRateLimiterBackend
    import app.core.rate_limit as rate_limit_module

    rate_limit_module._backend = InMemoryRateLimiterBackend()
    yield


def pytest_sessionfinish(session, exitstatus):
    """Clean up the shared temp SQLite file used by TestClient-based tests."""
    try:
        os.close(_TEST_DB_FD)
        os.unlink(_TEST_DB_PATH)
    except OSError:
        pass
