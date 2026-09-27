from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.db.session import check_database_connection

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check() -> dict:
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
    }


@router.get("/health/db")
def database_health_check() -> JSONResponse:
    """Verifies live connectivity to the configured database."""
    is_healthy, error = check_database_connection()

    payload = {
        "status": "ok" if is_healthy else "unavailable",
        "database": "sqlite" if settings.is_sqlite else "postgresql",
    }
    if error:
        payload["error"] = error

    return JSONResponse(
        content=payload,
        status_code=status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
    )


@router.get("/health/live")
def liveness_check() -> dict:
    """Kubernetes liveness probe: 'is this process alive and able to
    respond at all?' Deliberately checks nothing but the process itself —
    no DB, no external calls. If this ever fails to return, the orchestrator
    should kill and restart the pod; it should NOT fail just because a
    downstream dependency (e.g. the database) is temporarily down, or a
    healthy pod would get killed for someone else's outage."""
    return {"status": "alive"}


@router.get("/health/ready")
def readiness_check() -> JSONResponse:
    """Kubernetes readiness probe: 'can this instance actually serve
    traffic right now?' Unlike liveness, this DOES check the database —
    an instance that can't reach its DB should be taken out of the load
    balancer's rotation (but not killed; it may recover on its own)."""
    is_healthy, error = check_database_connection()

    payload = {"status": "ready" if is_healthy else "not_ready", "checks": {"database": is_healthy}}
    if error:
        payload["error"] = error

    return JSONResponse(
        content=payload,
        status_code=status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
    )
