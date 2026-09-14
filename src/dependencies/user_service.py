from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.clients import ServicePhoneClient
from src.config import (
    RedisCache,
)
from src.services import UserService
from .redis import get_redis
from .service_phone_client import get_service_phone_client
from .session_factory import get_session_factory
from .uow import get_uow


def get_user_service(
    session_factory: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_session_factory)
    ],
    redis: Annotated[RedisCache, Depends(get_redis)],
    service_phone_client: Annotated[
        ServicePhoneClient, Depends(get_service_phone_client)
    ],
) -> UserService:
    uow_factory = get_uow(session_factory=session_factory)
    return UserService(
        phone_client=service_phone_client,
        uow_factory=uow_factory,
        redis=redis,
    )
