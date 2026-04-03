from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.categories import router as categories_router
from app.api.v1.endpoints.daily_plans import router as daily_plans_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.notifications import router as notifications_router
from app.api.v1.endpoints.tasks import router as tasks_router
from app.api.v1.endpoints.time_logs import router as time_logs_router
from app.api.v1.endpoints.users import router as users_router

router = APIRouter()
router.include_router(health_router)
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(tasks_router)
router.include_router(categories_router)
router.include_router(time_logs_router)
router.include_router(daily_plans_router)
router.include_router(notifications_router)
