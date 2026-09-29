from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.config import UnitOfWork, RepositoryFactory


def get_uow_factory(session_factory: async_sessionmaker[AsyncSession]):
    return lambda: UnitOfWork(session_factory=session_factory)


def get_repository_factory() -> RepositoryFactory:
    return RepositoryFactory()
