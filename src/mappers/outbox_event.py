import uuid
from datetime import datetime, timezone
from typing import Any

from models import Notification
from src.models import OutboxEvent, OutboxStatus
from src.schemas import (
    SentNotificationResult,
    OutboxEventSchema,
)


def orm_to_dicts(
    events: list[OutboxEvent], status: OutboxStatus
) -> list[dict[str, Any]]:
    return [
        {
            "uuid": event.uuid,
            "status": status,
            "retry_count": event.retry_count,
            "next_retry_at": event.next_retry_at,
            "processing_started_at": datetime.now(timezone.utc),
            "attempt_id": uuid.uuid4(),
        }
        for event in events
    ]


def schema_to_dicts(results: list[SentNotificationResult]) -> list[dict[str, str]]:
    return [user.model_dump() for user in results]


def orm_to_dict(notification: Notification) -> dict[str, Any]:
    event = OutboxEventSchema(
        user_uuid=notification.user_uuid,
        notification_uuid=notification.uuid,
        type=notification.type,
        title=notification.title,
        message=notification.message,
    )
    return event.model_dump(mode="json")
