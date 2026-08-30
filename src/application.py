from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from src.clients import ServicePhoneClient
from src.config import (
    create_engine,
    create_session_factory,
    RedisCache,
    RetryBudgetStrategy,
    settings,
)
from src.handlers import register_errors_handlers


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        _app.state.redis = RedisCache(
            redis_url=str(settings.redis.url),
            cache_ttl_seconds=settings.redis.cache_ttl_seconds,
            socket_timeout=settings.redis.socket_timeout,
            socket_connect_timeout=settings.redis.socket_connect_timeout,
        )
        _app.state.engine = create_engine(settings.db.url)
        _app.state.session_factory = create_session_factory(
            engine=app.state.engine,
        )
        _app.state.client = httpx.AsyncClient(
            base_url=settings.client.base_url,
            timeout=settings.client.timeout,
        )
        _app.state.retry_strategy = RetryBudgetStrategy(
            retry_cost=settings.retry.retry_cost,
            retry_budget_ratio=settings.retry.retry_budget_ratio,
            max_retry_budget=settings.retry.max_retry_budget,
        )
        _app.state.service_phone_client = ServicePhoneClient(
            client=_app.state.client,
            retry_strategy=_app.state.retry_strategy,
        )
        yield

        await _app.state.redis.close()
        await _app.state.engine.dispose()
        await _app.state.client.aclose()

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
