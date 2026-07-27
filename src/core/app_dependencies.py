from dataclasses import dataclass

import httpx

from src.cache import RedisCache
from src.core.db import DatabaseManager
from src.core.retry_strategy import RetryBudgetStrategy


@dataclass
class AppDependencies:
    db: DatabaseManager
    redis: RedisCache
    http_client: httpx.AsyncClient
    retry_strategy: RetryBudgetStrategy
