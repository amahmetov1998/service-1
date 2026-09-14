from datetime import timedelta
from typing import Any

from sqlalchemy import insert, select, or_, Result, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import OutboxEvent, EventType, TaskStatus


class OutboxEventRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def create_event(self, payload: dict[str, Any]) -> None:

        stmt = insert(OutboxEvent).values(
            payload=payload,
            event_type=EventType.NOTIFICATION_CREATE,
            status=TaskStatus.PENDING,
        )
        await self.session.execute(stmt)

    async def get_pending(self, limit):
        stmt = (
            select(OutboxEvent)
            .where(
                OutboxEvent.status == TaskStatus.PENDING,
                or_(
                    OutboxEvent.next_retry_at.is_(None),
                    OutboxEvent.next_retry_at <= func.now(),
                ),
            )
            .with_for_update(skip_locked=True)
            .limit(limit)
        )
        result: Result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_stuck(
        self, limit: int, processing_timeout: timedelta
    ) -> list[OutboxEvent]:
        stmt = (
            select(OutboxEvent)
            .where(
                OutboxEvent.status == TaskStatus.PROCESSING,
                OutboxEvent.processing_started_at <= func.now() - processing_timeout,
            )
            .with_for_update(skip_locked=True)
            .limit(limit)
        )
        result: Result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_events_status(self, events: list[dict[str, str]]) -> None:
        for event in events:
            stmt = (
                update(OutboxEvent)
                .where(OutboxEvent.uuid == event["uuid"])
                .values(
                    status=event["status"],
                    retry_count=event["retry_count"],
                    next_retry_at=event["next_retry_at"],
                    processing_started_at=event["processing_started_at"],
                )
            )
            await self.session.execute(stmt)

    async def update_processed_events_status(
        self, events: list[dict[str, str]]
    ) -> None:
        for event in events:
            stmt = (
                update(OutboxEvent)
                .where(
                    OutboxEvent.uuid == event["uuid"],
                    OutboxEvent.attempt_id == event["attempt_id"],
                )
                .values(
                    status=event["status"],
                    retry_count=event["retry_count"],
                    next_retry_at=event["next_retry_at"],
                    processing_started_at=None,
                )
            )
            await self.session.execute(stmt)
