import json

from redis.asyncio import Redis


class RedisCache:
    def __init__(self, redis_url: str, cache_ttl_seconds: int | None = None) -> None:
        self.redis = Redis.from_url(redis_url, decode_responses=True)
        self.cache_ttl_seconds = cache_ttl_seconds

    async def set(
        self,
        key: str,
        value: dict,
    ) -> None:
        await self.redis.set(key, json.dumps(value), ex=self.cache_ttl_seconds)

    async def get(self, key: str) -> dict | None:
        value = await self.redis.get(key)
        if value is not None:
            return json.loads(value)
        else:
            return None

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)

    async def close(self) -> None:
        await self.redis.aclose()
