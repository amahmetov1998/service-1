from typing import Annotated, AsyncGenerator
from fastapi import Depends
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.cache import RedisCache
from src.clients import PhoneClient
from src.core.db import DatabaseManager
from src.repositories import UserRepository
from src.services import UserService


def get_phone_client(
    request: Request,
) -> PhoneClient:
    return PhoneClient(
        client=request.app.state.http_client,
        retry_strategy=request.app.state.retry_strategy,
    )


def get_redis_backend(request: Request) -> RedisCache:
    return request.app.state.redis


def get_db_backend(request: Request) -> DatabaseManager:
    return request.app.state.db


async def get_session(
    db: Annotated[DatabaseManager, Depends(get_db_backend)],
) -> AsyncGenerator[AsyncSession, None]:
    async with db.session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserRepository:
    return UserRepository(
        session=session,
    )


def get_user_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    phone_client: Annotated[PhoneClient, Depends(get_phone_client)],
    redis: Annotated[RedisCache, Depends(get_redis_backend)],
) -> UserService:
    return UserService(
        phone_client=phone_client,
        user_repository=user_repository,
        redis=redis,
    )
