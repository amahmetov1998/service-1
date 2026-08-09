from typing import Annotated

from fastapi import Depends

from src.config import AppDependencies
from src.config import RedisCache
from src.dependencies import get_dependencies


def get_redis_backend(
    deps: Annotated[AppDependencies, Depends(get_dependencies)],
) -> RedisCache:
    return deps.redis
