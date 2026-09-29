import logging

from src.exceptions import NotFoundError
from src.mappers import outbox_event as outbox_event_mapper
from src.models import Notification, EventType, OutboxStatus
from src.repositories import (
    NotificationRepository,
    OutboxEventRepository,
    UserRepository,
)
from src.schemas import (
    NotificationCreateRequest,
)

log = logging.getLogger(__name__)


class NotificationService:
    def __init__(
        self,
        events: OutboxEventRepository,
        notifications: NotificationRepository,
        users: UserRepository,
    ) -> None:
        self.events = events
        self.notifications = notifications
        self.users = users

    async def create_notification(
        self, payload: NotificationCreateRequest
    ) -> Notification:
        user = await self.users.get_user(user_uuid=payload.user_uuid)
        if not user:
            log.warning("User does not exist with uuid=%s", payload.user_uuid)
            raise NotFoundError("User not found")

        notification = await self.notifications.create_notification(
            notification=Notification(**payload.model_dump())
        )
        event = outbox_event_mapper.orm_to_orm(
            notification=notification,
            event_type=EventType.NOTIFICATION_CREATE,
            status=OutboxStatus.PENDING,
        )
        await self.events.create_event(event=event)
        return notification
