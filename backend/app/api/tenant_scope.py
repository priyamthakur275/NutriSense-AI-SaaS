"""Multi-institution tenant isolation.

This is a distinct concern from app.api.rbac (which answers "can this
*role* perform this *action*") — this module answers "which specific
institution(s) does this *user* actually belong to", and enforces that a
caller can't act on or read another institution's data just by supplying
a different institution_id, regardless of what their role permits in the
abstract.

Context: Phase 5's final verification flagged that every institution_id-
scoped endpoint across the API only checked role-level permissions
(`reports:read`, `users:manage`, etc.), never whether the caller's
institution_id matched the one requested — a real cross-tenant read/write
gap. This module is the fix, applied as a drop-in replacement for the
raw `institution_id: UUID` parameter already used throughout Phase 4D/5
endpoints (see `verify_institution_scope`) rather than a rewrite of any
endpoint's business logic.

PARENT accounts derive their institution access transitively: Parent ->
ParentStudentLink -> Student -> Student.institution_id (see
app.models.parent_student_link). A parent has no institutional
affiliation of their own — their access exists only in service of their
linked child/children's records, and is scoped to exactly those
institutions, nothing broader.
"""

from uuid import UUID

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import AuthorizationError, ValidationAppError
from app.db.session import get_db
from app.models.parent_student_link import ParentStudentLink
from app.models.staff import Staff
from app.models.student import Student
from app.models.user import User, UserRole


def get_user_institution_ids(db: Session, user: User) -> set[UUID]:
    """Every institution this user is actually affiliated with — via a
    Student or Staff profile directly, or (for PARENT accounts)
    transitively through their linked children's institutions. A user
    could in principle have more than one of these simultaneously, though
    that's unusual. SUPER_ADMIN is handled separately by callers — this
    function returns the user's *actual* affiliations regardless of role,
    it does not itself grant platform-wide bypass.
    """
    student_ids = {
        row[0]
        for row in db.query(Student.institution_id).filter(
            Student.user_id == user.id, Student.deleted_at.is_(None)
        )
    }
    staff_ids = {
        row[0]
        for row in db.query(Staff.institution_id).filter(
            Staff.user_id == user.id, Staff.deleted_at.is_(None)
        )
    }
    parent_ids = {
        row[0]
        for row in db.query(Student.institution_id)
        .join(ParentStudentLink, ParentStudentLink.student_id == Student.id)
        .filter(ParentStudentLink.parent_user_id == user.id, Student.deleted_at.is_(None))
    }
    return student_ids | staff_ids | parent_ids


def user_can_access_institution(db: Session, user: User, institution_id: UUID) -> bool:
    if user.role == UserRole.SUPER_ADMIN:
        return True
    return institution_id in get_user_institution_ids(db, user)


def verify_object_institution_access(db: Session, user: User, object_institution_id: UUID) -> None:
    """For detail routes (`GET/PATCH/DELETE /meals/{id}` and similar) where
    the institution isn't a request parameter at all — it belongs to the
    record already fetched by primary key. Call this immediately after
    `repo.get_or_404(...)`, before returning or mutating the object:

        meal = repo.get_or_404(meal_id)
        verify_object_institution_access(db, current_user, meal.institution_id)
        ...

    Raises AuthorizationError if the caller isn't affiliated with the
    record's institution (SUPER_ADMIN always passes).
    """
    if not user_can_access_institution(db, user, object_institution_id):
        raise AuthorizationError("You do not have access to this record")


def verify_institution_scope(
    institution_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UUID:
    """Drop-in dependency replacing a raw `institution_id: UUID` query/path
    parameter. Usage:

        # Before:
        def list_meals(institution_id: UUID, db: Session = Depends(get_db)): ...

        # After:
        def list_meals(institution_id: UUID = Depends(verify_institution_scope), ...): ...

    Returns the same institution_id (so the rest of the function body is
    completely unchanged) after confirming the caller is actually
    affiliated with it, or is a SUPER_ADMIN.
    """
    if not user_can_access_institution(db, current_user, institution_id):
        raise AuthorizationError(
            "You do not have access to this institution's data"
        )
    return institution_id


def resolve_institution_scope(
    institution_id: UUID | None = Query(None, description="Filter by institution"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UUID | None:
    """Drop-in dependency for list endpoints where `institution_id` is an
    OPTIONAL filter (`institution_id: UUID | None = Query(None)`) — a more
    severe variant of the same gap `verify_institution_scope` fixes: if the
    caller simply omits the filter, they'd otherwise see every institution's
    records platform-wide, not just be blocked from one specific one.

    Behavior:
      - SUPER_ADMIN: passed through unchanged (`None` legitimately means
        "no filter, show everything" for this role).
      - Any other role with no institutional affiliation at all: rejected —
        there's nothing legitimate to scope results to.
      - Affiliated with exactly one institution: that institution is used
        automatically whether or not the caller specified it (and if they
        specified a *different* one, that's rejected, same as
        `verify_institution_scope`).
      - Affiliated with more than one institution (a user with both a
        Staff and Student profile, or multiple Staff profiles) and no
        `institution_id` given: rejected with a clear message asking the
        caller to disambiguate, rather than silently picking one or
        returning a combined result the underlying repository's exact-match
        filter can't express.
    """
    if current_user.role == UserRole.SUPER_ADMIN:
        return institution_id

    user_institutions = get_user_institution_ids(db, current_user)
    if not user_institutions:
        raise AuthorizationError("Your account has no institutional affiliation")

    if institution_id is not None:
        if institution_id not in user_institutions:
            raise AuthorizationError("You do not have access to this institution's data")
        return institution_id

    if len(user_institutions) == 1:
        return next(iter(user_institutions))

    raise ValidationAppError(
        "Your account is affiliated with multiple institutions — please specify institution_id"
    )
