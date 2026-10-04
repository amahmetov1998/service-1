from typing import Any

from src.models import OutboxEvent, Notification, EventType, OutboxStatus
from src.schemas import (
    OutboxEventSchema,
)
from src.schemas import SentNotificationResult


def schema_to_dicts(results: list[SentNotificationResult]) -> list[dict[str, Any]]:
    return [
        {
            "event_uuid": result.uuid,
            "event_attempt_id": result.attempt_id,
            "next_retry_at": result.next_retry_at,
            "status": result.status,
            "retry_count": result.retry_count,
        }
        for result in results
    ]


def orm_to_dicts(
    events: list[OutboxEvent], status: OutboxStatus
) -> list[dict[str, Any]]:
    return [
        {
            "event_uuid": event.uuid,
            "status": status,
            "retry_count": event.retry_count,
            "next_retry_at": event.next_retry_at,
            "processing_started_at": event.processing_started_at,
            "attempt_id": event.attempt_id,
        }
        for event in events
    ]


def orm_to_orm(
    notification: Notification, event_type: EventType, status: OutboxStatus
) -> OutboxEvent:
    event = OutboxEventSchema(
        user_uuid=notification.user_uuid,
        notification_uuid=notification.uuid,
        type=notification.type,
        title=notification.title,
        message=notification.message,
    )
    return OutboxEvent(
        event_type=event_type,
        status=status,
        payload=event.model_dump(mode="json"),
    )
