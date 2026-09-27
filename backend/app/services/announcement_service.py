"""Announcement broadcast: resolves the target audience into a concrete
set of recipient user_ids, creates the Announcement record (the campaign),
and fans out one Notification row per recipient — reusing the existing
Notification model/table (Phase 4D) rather than inventing a parallel
delivery mechanism. This is the "Institution broadcasts" / "Announcement
system" requirement built on top of what already exists, not a rewrite
of it.
"""

from sqlalchemy.orm import Session

from app.models.announcement import Announcement
from app.models.enums import AnnouncementAudience, NotificationType
from app.models.notification import Notification
from app.models.parent_student_link import ParentStudentLink
from app.models.staff import Staff
from app.models.student import Student
from app.models.user import User
from app.repositories.announcement import AnnouncementRepository
from app.schemas.announcement import AnnouncementCreate


def _resolve_recipients(db: Session, payload: AnnouncementCreate) -> set[str]:
    recipients: set[str] = set()

    student_query = db.query(Student.user_id).filter(
        Student.institution_id == payload.institution_id, Student.deleted_at.is_(None)
    )
    staff_query = db.query(Staff.user_id).filter(
        Staff.institution_id == payload.institution_id, Staff.deleted_at.is_(None)
    )
    if payload.department_id is not None:
        student_query = student_query.filter(Student.department_id == payload.department_id)
        staff_query = staff_query.filter(Staff.department_id == payload.department_id)

    if payload.audience in (AnnouncementAudience.ALL, AnnouncementAudience.STUDENTS):
        recipients.update(row[0] for row in student_query)

    if payload.audience in (AnnouncementAudience.ALL, AnnouncementAudience.STAFF):
        recipients.update(row[0] for row in staff_query)

    if payload.audience in (AnnouncementAudience.ALL, AnnouncementAudience.PARENTS):
        parent_query = (
            db.query(ParentStudentLink.parent_user_id)
            .join(Student, Student.id == ParentStudentLink.student_id)
            .filter(Student.institution_id == payload.institution_id, Student.deleted_at.is_(None))
        )
        if payload.department_id is not None:
            parent_query = parent_query.filter(Student.department_id == payload.department_id)
        recipients.update(row[0] for row in parent_query)

    return recipients


async def send_announcement(db: Session, payload: AnnouncementCreate, *, created_by: User) -> Announcement:
    recipients = _resolve_recipients(db, payload)

    repo = AnnouncementRepository(db)
    announcement = repo.create(
        {
            "institution_id": payload.institution_id,
            "department_id": payload.department_id,
            "created_by_id": created_by.id,
            "audience": payload.audience,
            "title": payload.title,
            "body": payload.body,
            "recipient_count": len(recipients),
        }
    )

    created_notifications = []
    for user_id in recipients:
        notification = Notification(
            user_id=user_id,
            type=NotificationType.INFO,
            title=payload.title,
            message=payload.body,
        )
        db.add(notification)
        created_notifications.append(notification)

    db.commit()
    db.refresh(announcement)

    from app.realtime.notifier import publish_notification_created

    for notification in created_notifications:
        db.refresh(notification)
        await publish_notification_created(notification)

    return announcement
