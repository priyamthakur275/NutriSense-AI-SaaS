"""Domain model registry.

Every model must be imported here so that:
  1. `Base.metadata` is fully populated for Alembic autogenerate, and
  2. SQLAlchemy's mapper configuration step (which resolves the string-based
     relationship() targets used throughout these models) has every class
     available when it runs.

Import order matters only in that this module itself must be imported before
`Base.metadata.create_all()` / Alembic autogenerate / mapper configuration
is triggered — the order of the imports below does not matter, since all
inter-model references use TYPE_CHECKING + string relationship targets.
"""

from app.models.ai_recommendation import AIRecommendation
from app.models.announcement import Announcement
from app.models.attendance import Attendance
from app.models.audit_log import AuditLog
from app.models.chat_conversation import ChatConversation
from app.models.chat_message import ChatMessage
from app.models.chat_room import ChatRoom
from app.models.chat_room_member import ChatRoomMember
from app.models.compliance_report import ComplianceReport, compliance_report_meals
from app.models.department import Department
from app.models.email_verification_token import EmailVerificationToken
from app.models.institution import Institution
from app.models.institution_settings import InstitutionSettings
from app.models.meal import Meal
from app.models.meal_image import MealImage
from app.models.notification import Notification
from app.models.nutrition_profile import NutritionProfile
from app.models.nutrition_record import NutritionRecord
from app.models.parent_student_link import ParentStudentLink
from app.models.password_reset_token import PasswordResetToken
from app.models.refresh_token import RefreshToken
from app.models.room_message import RoomMessage
from app.models.staff import Staff
from app.models.student import Student
from app.models.user import User, UserRole
from app.models.user_invite import UserInvite
from app.models.user_settings import UserSettings

__all__ = [
    "AIRecommendation",
    "Announcement",
    "Attendance",
    "AuditLog",
    "ChatConversation",
    "ChatMessage",
    "ChatRoom",
    "ChatRoomMember",
    "ComplianceReport",
    "compliance_report_meals",
    "Department",
    "EmailVerificationToken",
    "Institution",
    "InstitutionSettings",
    "Meal",
    "MealImage",
    "Notification",
    "NutritionProfile",
    "NutritionRecord",
    "ParentStudentLink",
    "PasswordResetToken",
    "RefreshToken",
    "RoomMessage",
    "Staff",
    "Student",
    "User",
    "UserRole",
    "UserInvite",
    "UserSettings",
]
