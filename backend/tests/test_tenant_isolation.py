"""Multi-institution tenant isolation regression tests.

Guards against the cross-tenant read/write gap identified in the Phase 5
final verification report: an institution_id supplied by the client must
be checked against the caller's actual institutional affiliation, not
just their role-level permission.
"""

import pytest

from app.api.tenant_scope import get_user_institution_ids, user_can_access_institution
from app.models.enums import AIRecommendationStatus
from app.models.user import UserRole


def test_user_with_no_profile_has_no_institution_access(db_session, make_user, make_institution):
    user = make_user()
    institution = make_institution()

    assert get_user_institution_ids(db_session, user) == set()
    assert not user_can_access_institution(db_session, user, institution.id)


def test_staff_profile_grants_access_to_their_institution_only(
    db_session, make_user, make_institution
):
    from app.models.staff import Staff

    user = make_user(role=UserRole.ADMIN)
    own_institution = make_institution("Own Institution")
    other_institution = make_institution("Other Institution")

    staff = Staff(user_id=user.id, institution_id=own_institution.id, employee_id="EMP-001")
    db_session.add(staff)
    db_session.commit()

    assert user_can_access_institution(db_session, user, own_institution.id)
    assert not user_can_access_institution(db_session, user, other_institution.id)


def test_student_profile_grants_access_to_their_institution_only(
    db_session, make_user, make_institution, make_student
):
    user = make_user()
    own_institution = make_institution("Own Institution")
    other_institution = make_institution("Other Institution")
    make_student(user, own_institution)

    assert user_can_access_institution(db_session, user, own_institution.id)
    assert not user_can_access_institution(db_session, user, other_institution.id)


def test_super_admin_bypasses_institution_scoping(db_session, make_user, make_institution):
    super_admin = make_user(role=UserRole.SUPER_ADMIN)
    any_institution = make_institution()

    # No Staff/Student profile at all, yet access is still granted.
    assert get_user_institution_ids(db_session, super_admin) == set()
    assert user_can_access_institution(db_session, super_admin, any_institution.id)


class TestResolveInstitutionScope:
    """`resolve_institution_scope` covers list endpoints, where the more
    severe version of the gap lived: omitting the filter entirely used to
    mean "see every institution's records platform-wide", not just "you
    can't access one specific other institution".
    """

    def test_super_admin_with_no_filter_gets_unrestricted_none(self, db_session, make_user):
        from app.api.tenant_scope import resolve_institution_scope

        super_admin = make_user(role=UserRole.SUPER_ADMIN)
        result = resolve_institution_scope(institution_id=None, db=db_session, current_user=super_admin)
        assert result is None

    def test_user_with_no_affiliation_is_rejected(self, db_session, make_user):
        from app.api.tenant_scope import resolve_institution_scope
        from app.core.exceptions import AuthorizationError

        user = make_user(role=UserRole.STAFF)
        with pytest.raises(AuthorizationError):
            resolve_institution_scope(institution_id=None, db=db_session, current_user=user)

    def test_user_with_one_institution_defaults_to_it(self, db_session, make_user, make_institution):
        from app.models.staff import Staff
        from app.api.tenant_scope import resolve_institution_scope

        user = make_user(role=UserRole.STAFF)
        institution = make_institution()
        db_session.add(Staff(user_id=user.id, institution_id=institution.id, employee_id="EMP-001"))
        db_session.commit()

        result = resolve_institution_scope(institution_id=None, db=db_session, current_user=user)
        assert result == institution.id

    def test_user_requesting_other_institution_is_rejected(self, db_session, make_user, make_institution):
        from app.models.staff import Staff
        from app.api.tenant_scope import resolve_institution_scope
        from app.core.exceptions import AuthorizationError

        user = make_user(role=UserRole.STAFF)
        own = make_institution("Own")
        other = make_institution("Other")
        db_session.add(Staff(user_id=user.id, institution_id=own.id, employee_id="EMP-002"))
        db_session.commit()

        with pytest.raises(AuthorizationError):
            resolve_institution_scope(institution_id=other.id, db=db_session, current_user=user)

    def test_user_with_multiple_institutions_and_no_filter_must_disambiguate(
        self, db_session, make_user, make_institution
    ):
        from app.models.staff import Staff
        from app.models.student import Student
        from app.api.tenant_scope import resolve_institution_scope
        from app.core.exceptions import ValidationAppError

        user = make_user(role=UserRole.STAFF)
        inst_1 = make_institution("First")
        inst_2 = make_institution("Second")
        db_session.add(Staff(user_id=user.id, institution_id=inst_1.id, employee_id="EMP-003"))
        db_session.add(Student(user_id=user.id, institution_id=inst_2.id, enrollment_number="ENR-999"))
        db_session.commit()

        with pytest.raises(ValidationAppError):
            resolve_institution_scope(institution_id=None, db=db_session, current_user=user)
