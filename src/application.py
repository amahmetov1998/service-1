import httpx

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from api import router as api_router

from contextlib import asynccontextmanager

from utils.db_helper import db_helper

from errors_handlers import register_errors_handlers


@asynccontextmanager
async def lifespan(_app: FastAPI):
    _app.state.http_client = httpx.AsyncClient(
        base_url="http://localhost:8080",
        timeout=10,
    )
    yield
    await db_helper.dispose()
    await _app.state.http_client.aclose()


def get_app() -> FastAPI:
    app = FastAPI(
        lifespan=lifespan,
        docs_url="/docs",
        openapi_url="/openapi.json",
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
