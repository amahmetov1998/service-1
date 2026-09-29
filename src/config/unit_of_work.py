from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories import (
    UserRepository,
    PhoneRepository,
    NotificationRepository,
    OutboxEventRepository,
)


class UnitOfWork:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()
        self._transaction = await self.session.begin()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await self._transaction.__aexit__(
                exc_type,
                exc_val,
                exc_tb,
            )
        finally:
            await self.session.close()


class RepositoryFactory:
    def notification(self, session: AsyncSession) -> NotificationRepository:
        return NotificationRepository(session)

    def phone(self, session: AsyncSession) -> PhoneRepository:
        return PhoneRepository(session)

    def outbox_event(self, session: AsyncSession) -> OutboxEventRepository:
        return OutboxEventRepository(session)

    def user(self, session: AsyncSession) -> UserRepository:
        return UserRepository(session)
