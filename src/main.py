import asyncio
import logging

import uvicorn
from fastapi import FastAPI

from src.api import healthcheck_router, user_phones_router, notification_router
from src.application import create_app
from src.config import configure_logging
from src.config import settings
from src.handlers import register_errors_handlers

configure_logging(settings.logging)

log = logging.getLogger(__name__)


def get_app() -> FastAPI:

    app: FastAPI = create_app()
    register_errors_handlers(app)
    app.include_router(healthcheck_router)
    app.include_router(user_phones_router)
    app.include_router(notification_router)
    return app


async def main() -> None:
    uvicorn.run(
        "main:get_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=settings.run.reload,
        factory=settings.run.factory,
    )


if __name__ == "__main__":
    asyncio.run(main())
