from fastapi import APIRouter

from app.api.v1 import (
    achievements,
    ai,
    auth,
    certificates,
    courses,
    exercises,
    health,
    manage,
    notifications,
    progress,
    projects,
    reviews,
    users,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(courses.router)
api_router.include_router(progress.router)
api_router.include_router(exercises.router)
api_router.include_router(ai.router)
api_router.include_router(projects.router)
api_router.include_router(reviews.router)
api_router.include_router(achievements.router)
api_router.include_router(manage.router)
api_router.include_router(notifications.router)
api_router.include_router(certificates.router)
