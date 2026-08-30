from fastapi import Request

from src.config import RedisCache


def get_redis(
    request: Request,
) -> RedisCache:
    return request.app.state.redis
