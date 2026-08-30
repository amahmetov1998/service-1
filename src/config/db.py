from pydantic import PostgresDsn
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine,
)

from .config import settings


def create_engine(url: PostgresDsn) -> AsyncEngine:
    return create_async_engine(
        url=str(url),
        echo=settings.db.echo,
        echo_pool=settings.db.echo_pool,
        pool_pre_ping=settings.db.pool_pre_ping,
        pool_size=settings.db.pool_size,
        max_overflow=settings.db.max_overflow,
    )


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
        autocommit=False,
        class_=AsyncSession,
    )
