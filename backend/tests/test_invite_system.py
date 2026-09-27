"""Invite lifecycle: create -> (mock) email -> accept -> profile auto-
creation -> single-use enforcement, plus restore (soft-delete reversal)."""

import pytest

from app.core.exceptions import DuplicateResourceError, InvalidTokenError, ValidationAppError
from app.models.enums import InstitutionType
from app.models.user import UserRole
from app.schemas.invite import InviteAccept, InviteCreate
from app.services import invite_service
from app.services.email_service import ConsoleEmailService


def test_invite_create_and_accept_creates_user_and_student_profile(db_session, make_user, make_institution):
    from app.models.student import Student

    admin = make_user(role=UserRole.ADMIN)
    institution = make_institution()

    invite, raw_token = invite_service.create_invite(
        db_session,
        InviteCreate(email="newperson@test.com", role=UserRole.STUDENT, institution_id=institution.id),
        invited_by=admin,
        email_service=ConsoleEmailService(),
    )
    assert invite.status.value == "pending"

    user, access_token, refresh_token = invite_service.accept_invite(
        db_session,
        InviteAccept(token=raw_token, full_name="New Person", password="NewPersonPass123"),
    )

    assert user.email == "newperson@test.com"
    assert user.role == UserRole.STUDENT
    assert access_token and refresh_token

    student = db_session.query(Student).filter(Student.user_id == user.id).first()
    assert student is not None
    assert student.institution_id == institution.id


def test_invite_token_is_single_use(db_session, make_user, make_institution):
    admin = make_user(role=UserRole.ADMIN)
    institution = make_institution()

    _, raw_token = invite_service.create_invite(
        db_session,
        InviteCreate(email="onceonly@test.com", role=UserRole.STUDENT, institution_id=institution.id),
        invited_by=admin,
        email_service=ConsoleEmailService(),
    )
    invite_service.accept_invite(
        db_session, InviteAccept(token=raw_token, full_name="First", password="FirstPass123")
    )

    with pytest.raises(InvalidTokenError):
        invite_service.accept_invite(
            db_session, InviteAccept(token=raw_token, full_name="Second", password="SecondPass123")
        )


def test_invite_rejected_for_already_registered_email(db_session, make_user, make_institution):
    admin = make_user(role=UserRole.ADMIN)
    institution = make_institution()
    existing = make_user()  # has a real email from the fixture

    with pytest.raises(DuplicateResourceError):
        invite_service.create_invite(
            db_session,
            InviteCreate(email=existing.email, role=UserRole.STUDENT, institution_id=institution.id),
            invited_by=admin,
            email_service=ConsoleEmailService(),
        )


class TestRestore:
    def test_restore_reverses_soft_delete(self, db_session, make_user):
        from app.repositories.user import UserRepository

        user = make_user()
        repo = UserRepository(db_session)

        repo.delete(user)
        assert repo.get(user.id) is None  # excluded from normal queries once deleted

        deleted = repo.get_deleted_or_404(user.id)
        restored = repo.restore(deleted)

        assert restored.deleted_at is None
        assert repo.get(user.id) is not None  # visible again

    def test_restoring_an_active_row_is_rejected(self, db_session, make_user):
        from app.repositories.user import UserRepository

        user = make_user()
        repo = UserRepository(db_session)

        with pytest.raises(ValidationAppError):
            repo.get_deleted_or_404(user.id)  # never deleted in the first place

    def test_restoring_nonexistent_id_is_not_found(self, db_session, make_user):
        import uuid
        from app.repositories.user import UserRepository
        from app.core.exceptions import NotFoundError

        repo = UserRepository(db_session)
        with pytest.raises(NotFoundError):
            repo.get_deleted_or_404(str(uuid.uuid4()))
