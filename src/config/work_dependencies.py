from dataclasses import dataclass

import httpx
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, AsyncEngine

from src.config.retry_strategy import RetryBudgetStrategy


@dataclass
class WorkDependencies:
    engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]
    http_client: httpx.AsyncClient
    retry_strategy: RetryBudgetStrategy
