"""Custom OpenAPI schema generation: JWT bearer security scheme (so
Swagger UI's "Authorize" button accepts a pasted access token) and tag
metadata (so /docs groups endpoints with a one-line description per
resource instead of an unlabeled flat list).

A note on why this is a security-scheme override rather than relying on
FastAPI's automatic detection: our login endpoint accepts a JSON body
(email/password), not the OAuth2 spec's form-urlencoded username/password.
FastAPI would normally infer an OAuth2 "password flow" Authorize dialog
from `OAuth2PasswordBearer`, but that flow expects to POST directly to
`tokenUrl` in that exact form encoding — it doesn't match our actual login
contract. `HTTPBearer` instead gives Swagger UI a simple "paste your JWT"
dialog, which matches how every real client (including the frontend)
authenticates: `Authorization: Bearer <token>`.

This only affects the *documentation* Swagger renders — it does not change
which endpoints actually require authentication. That enforcement already
happens at runtime via `Depends(get_current_user)` / `Depends(require_permission(...))`
in app.api.deps / app.api.rbac; this module only makes Swagger *display*
the lock icon accurately for operations that carry one of those
dependencies, and lets /docs) exercise them without hand-crafting curl calls.
"""

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

TAGS_METADATA = [
    {"name": "Health", "description": "Liveness, readiness, and database connectivity checks. Unauthenticated."},
    {"name": "Authentication", "description": "Registration, login, token refresh, password reset, and email verification."},
    {"name": "Users", "description": "Account management. Most operations require the `users:read` or `users:manage` permission."},
    {"name": "Institutions", "description": "Tenant organizations (schools, hospitals, hostels, canteens)."},
    {"name": "Departments", "description": "Sub-units within an institution (a hostel block, a school wing)."},
    {"name": "Students", "description": "Student profile records, one-to-one with a User account."},
    {"name": "Staff", "description": "Staff profile records (canteen managers, nutritionists, wardens)."},
    {"name": "Meals", "description": "Served meal events — the hub every image, nutrition record, and attendance entry links to."},
    {"name": "Meal Images", "description": "Captured tray photographs associated with a Meal."},
    {"name": "Nutrition Records", "description": "The aggregated nutrition profile computed for a Meal (one-to-one)."},
    {"name": "Attendance", "description": "Records of a user being present for a specific Meal."},
    {"name": "Compliance Reports", "description": "Periodic institutional compliance summaries covering a set of Meals."},
    {"name": "Notifications", "description": "In-app notifications. Owners can always manage their own regardless of role."},
    {"name": "AI Recommendations", "description": "Agent-generated recommendations and their human review status. CRUD only — no inference in this phase."},
    {"name": "User Settings", "description": "Per-user preferences (theme, notification channels, locale)."},
    {"name": "AI Vision", "description": "Food image analysis: detection and nutrition estimation via multi-provider LLM vision."},
    {"name": "Nutrition Profile", "description": "Per-user health/fitness profile (age, gender, height, weight, activity level, medical conditions, allergies, diet preference, fitness goal) driving personalized recommendations."},
    {"name": "AI Chat", "description": "Conversational nutrition assistant with context-aware, multi-turn chat history."},
    {"name": "AI Reports", "description": "Chart-ready analytics: nutrition trends, deficiency detection, attendance-vs-nutrition correlation, institution dashboards, and student insights. All figures are deterministic SQL aggregates; narrative text is the only AI-generated field."},
    {"name": "Institution Settings", "description": "Per-institution branding (logo, color, custom domain) and feature-flag configuration."},
    {"name": "Parent Links", "description": "Links between Parent-role accounts and their Student(s) — the source of a parent's institutional access."},
    {"name": "Announcements", "description": "Institution broadcasts, fanning out to Students/Staff/Parents (or all three) as in-app notifications."},
    {"name": "Admin Dashboard", "description": "Platform-operator views (Super Admin only): cross-institution metrics, AI usage, and the audit activity log."},
    {"name": "User Invites", "description": "Invite-based onboarding: an admin invites by email; the invitee proves control of it via a token and sets their own password."},
]

# Paths that are genuinely public — no Authorization header is ever
# required — so Swagger shouldn't show a lock icon on them.
_PUBLIC_PATH_PREFIXES = (
    "/api/v1/health",
    "/api/v1/auth/register",
    "/api/v1/auth/login",
    "/api/v1/auth/refresh",
    "/api/v1/auth/forgot-password",
    "/api/v1/auth/reset-password",
    "/api/v1/auth/verify-email",
    "/api/v1/invites/accept",
)


def _is_public_path(path: str) -> bool:
    return any(path == prefix or path.startswith(prefix) for prefix in _PUBLIC_PATH_PREFIXES)


def custom_openapi(app: FastAPI) -> dict:
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=TAGS_METADATA,
        contact={"name": "NutriSense AI Engineering", "email": "engineering@nutrisense.ai"},
        license_info={"name": "Proprietary"},
    )

    schema.setdefault("components", {}).setdefault("securitySchemes", {})["bearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "Paste the access token returned by /auth/login or /auth/register.",
    }

    for path, operations in schema.get("paths", {}).items():
        if _is_public_path(path):
            continue
        for method, operation in operations.items():
            if method not in {"get", "post", "put", "patch", "delete"}:
                continue
            operation["security"] = [{"bearerAuth": []}]

    app.openapi_schema = schema
    return app.openapi_schema
