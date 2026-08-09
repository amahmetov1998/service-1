from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from src.api import healthcheck_router, user_phones_router
from src.config import AppDependencies
from src.handlers import register_errors_handlers


def create_app(
    deps: AppDependencies,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        _app.state.deps = deps
        app.include_router(healthcheck_router)
        app.include_router(user_phones_router)
        yield

        await deps.engine.dispose()
        await deps.http_client.aclose()
        await deps.redis.close()

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

    register_errors_handlers(app)
    return app
