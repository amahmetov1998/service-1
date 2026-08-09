from typing import Annotated, Callable

from fastapi import Depends

from src.clients import PhoneClient
from src.config import RedisCache, UnitOfWork
from src.services import UserService
from .cache import get_redis_backend
from .client import get_phone_client
from .unit_of_work import get_uow


def get_user_service(
    uow_factory: Annotated[Callable[[], UnitOfWork], Depends(get_uow)],
    phone_client: Annotated[PhoneClient, Depends(get_phone_client)],
    redis: Annotated[RedisCache, Depends(get_redis_backend)],
) -> UserService:
    return UserService(
        phone_client=phone_client,
        uow_factory=uow_factory,
        redis=redis,
    )
