import httpx

from src.cache import RedisCache
from src.config import settings
from src.core.db import DatabaseManager
from src.core.app_dependencies import AppDependencies
from src.core.retry_strategy import RetryBudgetStrategy


def create_dependencies() -> AppDependencies:
    return AppDependencies(
        db=DatabaseManager(
            url=str(settings.db.url),
            echo=settings.db.echo,
            echo_pool=settings.db.echo_pool,
            max_overflow=settings.db.max_overflow,
            pool_size=settings.db.pool_size,
            pool_pre_ping=settings.db.pool_pre_ping,
        ),
        http_client=httpx.AsyncClient(
            base_url=settings.client.base_url,
            timeout=settings.client.timeout,
        ),
        redis=RedisCache(
            redis_url=str(settings.redis.url),
            cache_ttl_seconds=settings.redis.cache_ttl_seconds,
        ),
        retry_strategy=RetryBudgetStrategy(
            tokens_for_retry=settings.retry.tokens_for_retry,
            retry_budget_ratio=settings.retry.retry_budget_ratio,
            max_retries=settings.retry.max_retries_global,
        ),
    )
