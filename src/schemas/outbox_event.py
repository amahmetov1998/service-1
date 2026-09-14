from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import ConfigDict, BaseModel

from src.models import EventType, TaskStatus


class OutboxEventSchema(BaseModel):
    event_type: EventType
    message_id: UUID
    status: TaskStatus
    payload: dict[str, Any]
    retry_count: int
    next_retry_at: datetime | None
    processing_started_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class SentNotificationResult(BaseModel):
    uuid: UUID
    attempt_id: UUID
    next_retry_at: datetime | None
    status: TaskStatus | None
    retry_count: int
