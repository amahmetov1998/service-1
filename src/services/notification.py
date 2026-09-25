import logging
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.config import RepositoryFactory, NotificationContext
from src.dependencies import get_session_factory
from src.exceptions import NotFoundError
from src.mappers import outbox_event as outbox_event_mapper
from src.schemas import (
    NotificationCreateRequest,
    NotificationCreateResponse,
)

log = logging.getLogger(__name__)


class NotificationService:
    def __init__(
        self,
        session_factory: Annotated[
            async_sessionmaker[AsyncSession], Depends(get_session_factory)
        ],
        repo_factory: RepositoryFactory,
    ) -> None:
        self.session_factory = session_factory
        self.repo_factory = repo_factory

    @asynccontextmanager
    async def _tx(self):
        async with self.session_factory() as session:
            async with session.begin():
                yield NotificationContext(
                    session=session, repo_factory=self.repo_factory
                )

    async def create_notification(
        self, payload: NotificationCreateRequest
    ) -> NotificationCreateResponse:
        async with self._tx() as tx:
            user = await tx.users.get_user(user_uuid=payload.user_uuid)
            if not user:
                log.warning("User does not exist with uuid=%s", payload.user_uuid)
                raise NotFoundError("User not found")
            notification = await tx.notifications.create_notification(
                values=payload.model_dump()
            )
            event = outbox_event_mapper.orm_to_dict(notification=notification)
            await tx.events.create_event(event=event)
        return notification
