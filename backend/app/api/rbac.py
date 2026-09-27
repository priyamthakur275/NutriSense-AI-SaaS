"""Role-based access control: role -> permission mapping, plus the
dependency factories used to protect routes.

Two levels of granularity are supported:
  - `require_roles(*roles)`      — coarse: "any of these roles may proceed"
  - `require_permission(perm)`   — fine:   "the caller's role must grant
                                    this specific permission"

Prefer `require_permission` for business endpoints (a Nutritionist and an
Institution Admin might both need `meals:read`, but only the Admin should
have `users:manage`); `require_roles` remains useful for coarse checks like
"admin-only" areas.
"""

from __future__ import annotations

from collections.abc import Callable
from enum import Enum

from fastapi import Depends, HTTPException, status

from app.api.deps import get_current_user
from app.models.user import User, UserRole


class Permission(str, Enum):
    # --- Users & accounts ---
    USERS_READ = "users:read"
    USERS_MANAGE = "users:manage"  # create/deactivate/change role

    # --- Institution / org structure ---
    INSTITUTION_MANAGE = "institution:manage"
    DEPARTMENT_MANAGE = "department:manage"

    # --- Meals & nutrition ---
    MEALS_READ = "meals:read"
    MEALS_CREATE = "meals:create"
    NUTRITION_REVIEW = "nutrition:review"

    # --- Compliance & reporting ---
    REPORTS_READ = "reports:read"
    REPORTS_GENERATE = "reports:generate"

    # --- AI recommendations ---
    AI_RECOMMENDATIONS_READ = "ai_recommendations:read"
    AI_RECOMMENDATIONS_REVIEW = "ai_recommendations:review"

    # --- Attendance ---
    ATTENDANCE_READ = "attendance:read"
    ATTENDANCE_RECORD = "attendance:record"

    # --- Platform administration ---
    PLATFORM_ADMIN = "platform:admin"


# Role -> permission set. SUPER_ADMIN is handled as an implicit wildcard
# below rather than listed explicitly, so newly added permissions
# automatically apply to it without this table needing an update.
_ROLE_PERMISSIONS: dict[UserRole, frozenset[Permission]] = {
    UserRole.STUDENT: frozenset(
        {
            Permission.MEALS_READ,
            Permission.ATTENDANCE_READ,
        }
    ),
    UserRole.PARENT: frozenset(
        {
            Permission.MEALS_READ,
            Permission.ATTENDANCE_READ,
            Permission.REPORTS_READ,
        }
    ),
    UserRole.STAFF: frozenset(
        {
            Permission.MEALS_READ,
            Permission.MEALS_CREATE,
            Permission.ATTENDANCE_READ,
            Permission.ATTENDANCE_RECORD,
            Permission.USERS_READ,
        }
    ),
    UserRole.NUTRITIONIST: frozenset(
        {
            Permission.MEALS_READ,
            Permission.MEALS_CREATE,
            Permission.NUTRITION_REVIEW,
            Permission.REPORTS_READ,
            Permission.REPORTS_GENERATE,
            Permission.AI_RECOMMENDATIONS_READ,
            Permission.AI_RECOMMENDATIONS_REVIEW,
            Permission.ATTENDANCE_READ,
        }
    ),
    UserRole.ADMIN: frozenset(
        {
            # Institution Admin: everything within their institution except
            # platform-wide administration.
            Permission.USERS_READ,
            Permission.USERS_MANAGE,
            Permission.INSTITUTION_MANAGE,
            Permission.DEPARTMENT_MANAGE,
            Permission.MEALS_READ,
            Permission.MEALS_CREATE,
            Permission.NUTRITION_REVIEW,
            Permission.REPORTS_READ,
            Permission.REPORTS_GENERATE,
            Permission.AI_RECOMMENDATIONS_READ,
            Permission.AI_RECOMMENDATIONS_REVIEW,
            Permission.ATTENDANCE_READ,
            Permission.ATTENDANCE_RECORD,
        }
    ),
}


def get_permissions_for_role(role: UserRole) -> frozenset[Permission]:
    if role == UserRole.SUPER_ADMIN:
        return frozenset(Permission)
    return _ROLE_PERMISSIONS.get(role, frozenset())


def has_permission(role: UserRole, permission: Permission) -> bool:
    return permission in get_permissions_for_role(role)


def require_roles(*allowed_roles: UserRole) -> Callable[[User], User]:
    """Dependency factory: coarse role check. Superseded within app.api.deps
    by an identical helper kept for backward compatibility — this copy is
    the canonical one going forward; new endpoints should import from here."""

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return current_user

    return role_checker


def require_permission(permission: Permission) -> Callable[[User], User]:
    """Dependency factory: fine-grained permission check.

    Usage:
        @router.post("/meals", dependencies=[Depends(require_permission(Permission.MEALS_CREATE))])
    """

    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        if not has_permission(current_user.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires the '{permission.value}' permission",
            )
        return current_user

    return permission_checker
