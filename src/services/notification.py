import logging
from typing import Callable

from src.config import ApplicationUnitOfWork
from src.exceptions import NotFoundError
from src.schemas import NotificationCreateRequest, NotificationCreateResponse

log = logging.getLogger(__name__)


class NotificationService:
    def __init__(
        self,
        uow_factory: Callable[[], ApplicationUnitOfWork],
    ) -> None:
        self.uow_factory = uow_factory

    async def create_notification(
        self, payload: NotificationCreateRequest
    ) -> NotificationCreateResponse:
        async with self.uow_factory() as uow:
            user = await uow.users.get_user(user_uuid=payload.user_uuid)
            if not user:
                log.warning("User does not exist with uuid=%s", payload.user_uuid)
                raise NotFoundError("User not found")
            notification = await uow.notifications.create_notification(
                values=payload.model_dump()
            )
            await uow.events.create_event(payload.model_dump(mode="json"))
        return notification
