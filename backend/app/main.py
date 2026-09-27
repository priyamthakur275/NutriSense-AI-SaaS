from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.core.middleware import AuditMiddleware, RequestContextMiddleware, SecurityHeadersMiddleware
from app.core.openapi import TAGS_METADATA, custom_openapi
from app.db.session import dispose_db_connection, init_db_connection

configure_logging()
logger = get_logger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    description="AI-powered institutional food analysis, nutrition compliance, "
    "and multi-agent decision-support platform.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=TAGS_METADATA,
)
app.openapi = lambda: custom_openapi(app)  # type: ignore[method-assign]

register_exception_handlers(app)

# Middleware executes in reverse registration order for requests (last
# added runs first) and forward order for responses. Ordering here matters:
#   1. RequestContextMiddleware first (outermost) — every other layer's
#      logs, including CORS/GZip's own, should have the request ID
#      available and be covered by the timing measurement.
#   2. AuditMiddleware — writes an audit-trail row for mutations and
#      401/403 denials; grouped with RequestContextMiddleware since both
#      are pure observers of the request/response, not response-shapers.
#   3. SecurityHeadersMiddleware — applies to every response, including
#      error responses raised by inner layers.
#   4. GZip — compresses the final response body.
#   5. CORS — Starlette's CORSMiddleware short-circuits preflight OPTIONS
#      requests itself, so it should sit close to the application.
app.add_middleware(RequestContextMiddleware)
app.add_middleware(AuditMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1024)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.on_event("startup")
def on_startup() -> None:
    logger.info("%s starting in '%s' environment", settings.PROJECT_NAME, settings.ENVIRONMENT.value)
    init_db_connection()

    from app.realtime.handlers import register_realtime_handlers

    register_realtime_handlers()


@app.on_event("shutdown")
def on_shutdown() -> None:
    dispose_db_connection()
    logger.info("%s shutting down", settings.PROJECT_NAME)


import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import HTTPException

STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static"))
if os.path.isdir(os.path.join(STATIC_DIR, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")

@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
        raise HTTPException(status_code=404, detail="Not found")
        
    file_path = os.path.join(STATIC_DIR, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
        
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
        
    return {"message": "NutriSense AI API is running 🚀"}



if settings.METRICS_ENABLED:
    from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
    from starlette.responses import Response as StarletteResponse

    @app.get("/metrics", include_in_schema=False)
    def metrics() -> StarletteResponse:
        """Prometheus scrape target. Excluded from the OpenAPI schema (it's
        not a business API) and from authentication — Prometheus itself
        can't present a JWT, so this endpoint is expected to be firewalled
        at the network level (not exposed publicly) rather than
        JWT-protected, matching standard Prometheus deployment practice."""
        return StarletteResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)
