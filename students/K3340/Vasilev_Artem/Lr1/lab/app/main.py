from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from core.config import get_settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Future startup/shutdown hooks can be placed here.
    yield


def create_application() -> FastAPI:
    settings = get_settings()

    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )
    application.include_router(api_router)
    return application


app = create_application()
