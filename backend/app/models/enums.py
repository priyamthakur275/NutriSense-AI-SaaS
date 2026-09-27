"""Shared enums for domain models.

Centralized here (rather than duplicated per-model-file) so the same enum
can be reused across models without circular imports — e.g. MealStatus is
referenced by both Meal and, indirectly, reporting logic built on top of it.

`app.models.user.UserRole` is intentionally left in `user.py` — it predates
this module and moving it would touch an existing, already-migrated file
for no functional gain.
"""

import enum


class InstitutionType(str, enum.Enum):
    SCHOOL = "school"
    COLLEGE = "college"
    HOSPITAL = "hospital"
    HOSTEL = "hostel"
    CORPORATE = "corporate"
    GOVERNMENT = "government"


class MealType(str, enum.Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class MealStatus(str, enum.Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    ANALYZED = "analyzed"
    FAILED = "failed"


class AttendanceMethod(str, enum.Enum):
    FACE_RECOGNITION = "face_recognition"
    MANUAL = "manual"
    QR_CODE = "qr_code"


class ComplianceReportStatus(str, enum.Enum):
    DRAFT = "draft"
    FINAL = "final"


class NotificationType(str, enum.Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ALERT = "alert"


class AIRecommendationType(str, enum.Enum):
    MENU_CHANGE = "menu_change"
    PORTION_ADJUSTMENT = "portion_adjustment"
    INGREDIENT_SUBSTITUTION = "ingredient_substitution"
    GENERAL = "general"


class AIRecommendationStatus(str, enum.Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    APPLIED = "applied"
    DISMISSED = "dismissed"


class ThemePreference(str, enum.Enum):
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


class AuditAction(str, enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    ACCESS_DENIED = "access_denied"


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class ActivityLevel(str, enum.Enum):
    SEDENTARY = "sedentary"
    LIGHTLY_ACTIVE = "lightly_active"
    MODERATELY_ACTIVE = "moderately_active"
    VERY_ACTIVE = "very_active"
    EXTREMELY_ACTIVE = "extremely_active"


class DietPreference(str, enum.Enum):
    OMNIVORE = "omnivore"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    PESCATARIAN = "pescatarian"
    JAIN = "jain"
    HALAL = "halal"
    KOSHER = "kosher"


class FitnessGoal(str, enum.Enum):
    WEIGHT_LOSS = "weight_loss"
    WEIGHT_GAIN = "weight_gain"
    MUSCLE_GAIN = "muscle_gain"
    MAINTENANCE = "maintenance"
    GENERAL_HEALTH = "general_health"


class ChatRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"


class ParentRelationship(str, enum.Enum):
    MOTHER = "mother"
    FATHER = "father"
    GUARDIAN = "guardian"
    OTHER = "other"


class AnnouncementAudience(str, enum.Enum):
    ALL = "all"
    STUDENTS = "students"
    STAFF = "staff"
    PARENTS = "parents"


class InviteStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    REVOKED = "revoked"


class ChatRoomType(str, enum.Enum):
    DIRECT = "direct"
    GROUP = "group"
