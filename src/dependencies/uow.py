from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.config import ApplicationUnitOfWork


def get_uow(session_factory: async_sessionmaker[AsyncSession]):
    return lambda: ApplicationUnitOfWork(session_factory=session_factory)
