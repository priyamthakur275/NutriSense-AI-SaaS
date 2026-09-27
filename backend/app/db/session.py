from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def _build_engine() -> Engine:
    """Create the SQLAlchemy engine with environment-appropriate pooling.

    SQLite (used for lightweight local dev) doesn't support the pool sizing
    knobs used for Postgres, and requires check_same_thread=False when shared
    across FastAPI's threadpool.
    """
    if settings.is_sqlite:
        return create_engine(
            settings.DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=NullPool,
            echo=settings.DATABASE_ECHO,
        )

    return create_engine(
        settings.DATABASE_URL,
        poolclass=QueuePool,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        pool_timeout=settings.DATABASE_POOL_TIMEOUT,
        pool_recycle=settings.DATABASE_POOL_RECYCLE,
        pool_pre_ping=True,  # verifies connections aren't stale before use
        echo=settings.DATABASE_ECHO,
    )


engine = _build_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
Base = declarative_base()


def get_db() -> Generator:
    """FastAPI dependency that yields a scoped DB session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """Context-manager variant of `get_db` for use outside request handlers
    (scripts, background jobs, startup checks)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> tuple[bool, str | None]:
    """Attempt a lightweight round-trip query against the database.

    Returns (is_healthy, error_message). Used by the startup lifecycle hook
    and the /health/db endpoint — never raises.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, None
    except SQLAlchemyError as exc:
        logger.error("Database connectivity check failed: %s", exc)
        return False, str(exc)


def init_db_connection() -> None:
    """Verify DB connectivity at application startup. Logs and raises on
    failure so the app fails fast instead of serving requests against a
    broken database."""
    is_healthy, error = check_database_connection()
    if not is_healthy:
        logger.error("Startup database connectivity check failed: %s", error)
        raise RuntimeError(f"Could not connect to the database: {error}")
    logger.info("Database connection verified (%s)", "SQLite" if settings.is_sqlite else "PostgreSQL")


def dispose_db_connection() -> None:
    """Cleanly dispose of the connection pool on application shutdown."""
    engine.dispose()
    logger.info("Database connection pool disposed")
