import json
import logging

from redis import RedisError
from redis.asyncio import Redis

log = logging.getLogger(__name__)


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

    async def set(
        self,
        key: str,
        value: dict,
    ) -> None:
        payload = json.dumps(value)
        try:
            await self.redis.set(key, payload, ex=self.cache_ttl_seconds)
        except RedisError as e:
            log.warning("Redis SET failed for key=%s: %s", key, e)

    async def get(self, key: str) -> dict | None:
        try:
            value = await self.redis.get(key)
        except RedisError as e:
            log.warning("Redis GET failed for key=%s: %s", key, e)
            return None
        if value is None:
            return None
        return json.loads(value)

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)

    async def close(self) -> None:
        await self.redis.aclose()
