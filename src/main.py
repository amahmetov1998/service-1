import uvicorn
import asyncio

from fastapi import FastAPI

from application import create_app
from src.config import settings
from src.core.app_dependencies import AppDependencies
from src.core.factory import create_dependencies


def get_app() -> FastAPI:
    dependencies: AppDependencies = create_dependencies()
    app: FastAPI = create_app(dependencies)
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
