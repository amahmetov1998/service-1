from src.config import RedisCache, settings


def create_redis() -> RedisCache:
    return RedisCache(
        redis_url=str(settings.redis.url),
        cache_ttl_seconds=settings.redis.cache_ttl_seconds,
    )
