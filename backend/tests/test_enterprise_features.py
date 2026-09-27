"""Institution settings, parent-student linking (and its effect on tenant
scoping), and the announcement broadcast fan-out."""

import pytest

from app.models.enums import AnnouncementAudience, ParentRelationship
from app.models.user import UserRole


def test_institution_settings_lazy_create_and_defaults(db_session, make_institution):
    from app.services.institution_settings_service import get_or_create_settings

    institution = make_institution()
    settings = get_or_create_settings(db_session, institution.id)

    assert settings.institution_id == institution.id
    assert settings.feature_flags["ai_vision_analysis"] is True
    assert settings.is_feature_enabled("ai_vision_analysis") is True
    assert settings.is_feature_enabled("some_future_flag_not_yet_set") is False


def test_parent_gains_transitive_institution_access_via_link(
    db_session, make_user, make_institution, make_student
):
    from app.models.parent_student_link import ParentStudentLink
    from app.api.tenant_scope import user_can_access_institution

    parent = make_user(role=UserRole.PARENT)
    student_user = make_user(role=UserRole.STUDENT)
    institution = make_institution()
    student = make_student(student_user, institution)

    # Before linking: no access.
    assert not user_can_access_institution(db_session, parent, institution.id)

    db_session.add(
        ParentStudentLink(
            parent_user_id=parent.id,
            student_id=student.id,
            relationship_type=ParentRelationship.MOTHER,
        )
    )
    db_session.commit()

    # After linking: access granted transitively.
    assert user_can_access_institution(db_session, parent, institution.id)


@pytest.mark.asyncio
async def test_announcement_fans_out_to_correct_audience_only(
    db_session, make_user, make_institution, make_student
):
    from app.models.staff import Staff
    from app.models.notification import Notification
    from app.schemas.announcement import AnnouncementCreate
    from app.services.announcement_service import send_announcement

    institution = make_institution()
    admin = make_user(role=UserRole.ADMIN)
    student_user = make_user(role=UserRole.STUDENT)
    staff_user = make_user(role=UserRole.STAFF)
    make_student(student_user, institution)
    db_session.add(Staff(user_id=staff_user.id, institution_id=institution.id, employee_id="EMP-100"))
    db_session.commit()

    payload = AnnouncementCreate(
        institution_id=institution.id,
        audience=AnnouncementAudience.STUDENTS,
        title="Test broadcast",
        body="Only students should get this",
    )
    announcement = await send_announcement(db_session, payload, created_by=admin)

    assert announcement.recipient_count == 1
    student_notifications = (
        db_session.query(Notification).filter(Notification.user_id == student_user.id).all()
    )
    staff_notifications = db_session.query(Notification).filter(Notification.user_id == staff_user.id).all()

    assert len(student_notifications) == 1
    assert student_notifications[0].title == "Test broadcast"
    assert len(staff_notifications) == 0  # audience was STUDENTS only — staff must not receive it


@pytest.mark.asyncio
async def test_announcement_all_audience_reaches_students_and_staff(
    db_session, make_user, make_institution, make_student
):
    from app.models.staff import Staff
    from app.models.notification import Notification
    from app.schemas.announcement import AnnouncementCreate
    from app.services.announcement_service import send_announcement

    institution = make_institution()
    admin = make_user(role=UserRole.ADMIN)
    student_user = make_user(role=UserRole.STUDENT)
    staff_user = make_user(role=UserRole.STAFF)
    make_student(student_user, institution)
    db_session.add(Staff(user_id=staff_user.id, institution_id=institution.id, employee_id="EMP-101"))
    db_session.commit()

    payload = AnnouncementCreate(
        institution_id=institution.id,
        audience=AnnouncementAudience.ALL,
        title="Everyone broadcast",
        body="Students and staff both get this",
    )
    announcement = await send_announcement(db_session, payload, created_by=admin)

    assert announcement.recipient_count == 2
    assert db_session.query(Notification).filter(Notification.user_id == student_user.id).count() == 1
    assert db_session.query(Notification).filter(Notification.user_id == staff_user.id).count() == 1
