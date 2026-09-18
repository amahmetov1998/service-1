from uuid import UUID

from pydantic import BaseModel

from src.models import NotificationType


class OutboxEventSchema(BaseModel):
    notification_uuid: UUID
    user_uuid: UUID
    type: NotificationType
    title: str
    message: str
