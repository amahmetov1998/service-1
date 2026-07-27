from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from src.core.app_dependencies import AppDependencies
from src.api import router as api_router

from contextlib import asynccontextmanager

from src.core.errors_handlers import register_errors_handlers


def create_app(
    dependencies: AppDependencies,
) -> FastAPI:

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        _app.state.db = dependencies.db
        _app.state.http_client = dependencies.http_client
        _app.state.redis = dependencies.redis
        _app.state.retry_strategy = dependencies.retry_strategy
        yield
        await _app.state.db.dispose()
        await _app.state.http_client.aclose()
        await _app.state.redis.close()

    app = FastAPI(
        lifespan=lifespan,
        default_response_class=JSONResponse,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)
    register_errors_handlers(app)
    return app
