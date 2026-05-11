from fastapi import APIRouter

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.router import router as v1_router
from core.config import get_settings

settings = get_settings()

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(v1_router, prefix=settings.api_v1_prefix)
