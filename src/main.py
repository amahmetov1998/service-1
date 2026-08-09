import asyncio
import logging

import uvicorn
from fastapi import FastAPI

from src.application import create_app
from src.config import AppDependencies
from src.config import settings
from src.handlers import register_errors_handlers
from src.providers import create_app_dependencies

logging.basicConfig(
    level=settings.logging.log_level_value,
    format=settings.logging.log_format,
)

log = logging.getLogger(__name__)


def get_app() -> FastAPI:
    dependencies: AppDependencies = create_app_dependencies()
    app: FastAPI = create_app(dependencies)
    register_errors_handlers(app)
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
