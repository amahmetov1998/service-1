from typing import Self

from src.repositories import (
    UserRepository,
    PhoneRepository,
    NotificationRepository,
    OutboxEventRepository,
)


class UnitOfWork:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __aenter__(self) -> Self:
        self.session = self.session_factory()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            if exc_type is None:
                await self.session.commit()
            else:
                await self.session.rollback()
        finally:
            await self.session.close()


class ApplicationUnitOfWork(UnitOfWork):
    async def __aenter__(self) -> Self:
        await super().__aenter__()
        self.users = UserRepository(self.session)
        self.phones = PhoneRepository(self.session)
        self.notifications = NotificationRepository(self.session)
        self.events = OutboxEventRepository(self.session)
        return self
