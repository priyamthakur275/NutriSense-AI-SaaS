"""Invite lifecycle: create (hash-stored token, mock-emailed) and accept
(creates the User + role-appropriate profile, issues a session — reusing
the exact token-issuance mechanics auth_service uses for register/login,
not a parallel implementation of it).
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import DuplicateResourceError, InvalidTokenError
from app.core.security import create_access_token, generate_opaque_token, hash_opaque_token, hash_password
from app.models.enums import AuditAction, InviteStatus
from app.models.institution import Institution
from app.models.staff import Staff
from app.models.student import Student
from app.models.user import User, UserRole
from app.models.user_invite import UserInvite
from app.repositories.invite import UserInviteRepository
from app.schemas.invite import InviteAccept, InviteCreate
from app.services import token_service
from app.services.audit_service import log_audit_event
from app.services.email_service import EmailService, build_invite_email

INVITE_EXPIRE_HOURS = 72

# Roles that get an institution-linking profile automatically on accept.
_PROFILE_ROLES = {UserRole.STUDENT: Student, UserRole.STAFF: Staff, UserRole.ADMIN: Staff, UserRole.NUTRITIONIST: Staff}


def create_invite(
    db: Session, payload: InviteCreate, *, invited_by: User, email_service: EmailService
) -> tuple[UserInvite, str]:
    if db.query(User).filter(User.email == payload.email, User.deleted_at.is_(None)).first():
        raise DuplicateResourceError(f"A user with email '{payload.email}' already exists")

    institution = db.query(Institution).filter(Institution.id == payload.institution_id).first()
    institution_name = institution.name if institution else "your institution"

    raw_token = generate_opaque_token()
    repo = UserInviteRepository(db)
    invite = repo.create(
        {
            "email": payload.email,
            "role": payload.role,
            "institution_id": payload.institution_id,
            "department_id": payload.department_id,
            "invited_by_id": invited_by.id,
            "token_hash": hash_opaque_token(raw_token),
            "status": InviteStatus.PENDING,
            "expires_at": datetime.now(timezone.utc) + timedelta(hours=INVITE_EXPIRE_HOURS),
        }
    )

    subject, body = build_invite_email(institution_name=institution_name, role=payload.role.value, token=raw_token)
    email_service.send(to=payload.email, subject=subject, body=body)

    log_audit_event(
        db, user_id=invited_by.id, action=AuditAction.CREATE, entity_type="UserInvite", entity_id=str(invite.id)
    )
    db.commit()
    db.refresh(invite)
    return invite, raw_token


def accept_invite(db: Session, payload: InviteAccept) -> tuple[User, str, str]:
    invite = db.query(UserInvite).filter(UserInvite.token_hash == hash_opaque_token(payload.token)).first()
    if invite is None or not invite.is_valid:
        raise InvalidTokenError("This invitation is invalid or has expired")

    if db.query(User).filter(User.email == invite.email, User.deleted_at.is_(None)).first():
        raise DuplicateResourceError(f"A user with email '{invite.email}' already exists")

    user = User(full_name=payload.full_name, email=invite.email, hashed_password=hash_password(payload.password), role=invite.role)
    db.add(user)
    db.flush()

    profile_model = _PROFILE_ROLES.get(invite.role)
    if profile_model is Student:
        db.add(
            Student(
                user_id=user.id,
                institution_id=invite.institution_id,
                department_id=invite.department_id,
                enrollment_number=f"INV-{user.id[:8]}",
            )
        )
    elif profile_model is Staff:
        db.add(
            Staff(
                user_id=user.id,
                institution_id=invite.institution_id,
                department_id=invite.department_id,
                employee_id=f"INV-{user.id[:8]}",
            )
        )

    invite.status = InviteStatus.ACCEPTED
    invite.accepted_at = datetime.now(timezone.utc)

    access_token = create_access_token(subject=user.id, extra_claims={"role": user.role.value})
    refresh_token = token_service.issue_refresh_token(db, user)

    log_audit_event(db, user_id=user.id, action=AuditAction.CREATE, entity_type="User", entity_id=user.id, details={"via": "invite"})
    db.commit()
    db.refresh(user)
    return user, access_token, refresh_token
