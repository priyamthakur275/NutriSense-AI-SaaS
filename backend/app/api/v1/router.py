from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    ai_chat,
    ai_recommendation_engine,
    ai_recommendations,
    ai_reports,
    ai_vision,
    announcements,
    attendance,
    auth,
    chat_rooms,
    compliance_reports,
    departments,
    health,
    institution_settings,
    institutions,
    invites,
    meal_images,
    meals,
    notifications,
    nutrition_profile,
    nutrition_records,
    parent_links,
    staff,
    students,
    user_settings,
    users,
    ws,
)

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(institutions.router)
api_router.include_router(departments.router)
api_router.include_router(students.router)
api_router.include_router(staff.router)
api_router.include_router(meals.router)
api_router.include_router(meal_images.router)
api_router.include_router(nutrition_records.router)
api_router.include_router(attendance.router)
api_router.include_router(compliance_reports.router)
api_router.include_router(notifications.router)
api_router.include_router(ai_recommendations.router)
api_router.include_router(user_settings.router)
api_router.include_router(ai_vision.router)
api_router.include_router(nutrition_profile.router)
api_router.include_router(ai_recommendation_engine.router)
api_router.include_router(ai_chat.router)
api_router.include_router(ai_reports.router)
api_router.include_router(institution_settings.router)
api_router.include_router(parent_links.router)
api_router.include_router(announcements.router)
api_router.include_router(invites.router)
api_router.include_router(admin.router)
api_router.include_router(chat_rooms.router)
api_router.include_router(ws.router)
