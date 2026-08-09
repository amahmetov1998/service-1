from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories import UserRepository


def create_user_repository(
    session: AsyncSession,
) -> UserRepository:
    return UserRepository(session=session)
