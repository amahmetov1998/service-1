import uuid
from datetime import datetime, timezone
from typing import Any

from src.models import OutboxEvent, TaskStatus
from src.schemas import SentNotificationResult


def orm_to_dict(events: list[OutboxEvent], status: TaskStatus) -> list[dict[str, Any]]:
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


def schema_to_dict(results: list[SentNotificationResult]) -> list[dict[str, str]]:
    return [user.model_dump() for user in results]
