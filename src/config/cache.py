import functools
import json
import logging

from redis import RedisError
from redis.asyncio import Redis

log = logging.getLogger(__name__)


def handle_cache_errors(request_func):
    @functools.wraps(request_func)
    async def wrapper(*args, **kwargs):
        try:
            return await request_func(*args, **kwargs)
        except RedisError as e:
            log.warning(
                "Redis operation failed. Error type=%s, error=%s", type(e).__name__, e
            )
            return None

    return wrapper


class RedisCache:
    def __init__(
        self,
        redis_url: str,
        socket_connect_timeout: float,
        socket_timeout: float,
        cache_ttl_seconds: int | None = None,
    ) -> None:
        self.redis = Redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=socket_connect_timeout,
            socket_timeout=socket_timeout,
        )
        self.cache_ttl_seconds = cache_ttl_seconds

    @handle_cache_errors
    async def set(
        self,
        key: str,
        value: dict,
    ) -> None:
        payload = json.dumps(value)
        await self.redis.set(key, payload, ex=self.cache_ttl_seconds)

    @handle_cache_errors
    async def get(self, key: str) -> dict | None:
        value = await self.redis.get(key)
        result = json.loads(value) if value else None
        return result

    @handle_cache_errors
    async def delete(self, key: str) -> None:
        await self.redis.delete(key)

    async def close(self) -> None:
        await self.redis.aclose()
