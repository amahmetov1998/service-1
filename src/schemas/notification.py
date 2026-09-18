from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.models import OutboxStatus, NotificationType


class NotificationCreateRequest(BaseModel):
    user_uuid: UUID
    type: NotificationType
    title: str = Field(max_length=20)
    message: str = Field(max_length=200)


class NotificationCreateResponse(NotificationCreateRequest):
    pass


class SentNotificationResult(BaseModel):
    uuid: UUID
    attempt_id: UUID
    next_retry_at: datetime | None
    status: OutboxStatus | None
    retry_count: int
