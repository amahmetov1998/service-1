from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import Integer, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .enums import OutboxStatus, EventType


class OutboxEvent(Base):
    event_type: Mapped[EventType]
    message_id: Mapped[UUID] = mapped_column(default=uuid4)
    attempt_id: Mapped[UUID] = mapped_column(default=uuid4)
    status: Mapped[OutboxStatus]
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    next_retry_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    processing_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
