import logging
from contextlib import asynccontextmanager
from typing import Callable

from src.config import UnitOfWork, RepositoryFactory, NotificationContext
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
        uow_factory: Callable[[], UnitOfWork],
        repo_factory: RepositoryFactory,
    ) -> None:
        self.uow_factory = uow_factory
        self.repo_factory = repo_factory

    @asynccontextmanager
    async def _tx(self):
        async with self.uow_factory() as uow:
            yield NotificationContext(uow=uow, repo_factory=self.repo_factory)

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
