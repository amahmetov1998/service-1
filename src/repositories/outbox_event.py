from datetime import timedelta

from sqlalchemy import select, or_, Result, func, update, bindparam
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import OutboxEvent, OutboxStatus


class OutboxEventRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def create_event(self, event: OutboxEvent) -> OutboxEvent:
        self.session.add(event)
        return event

    async def get_pending(self, limit: int) -> list[OutboxEvent]:
        stmt = (
            select(OutboxEvent)
            .where(
                OutboxEvent.status == OutboxStatus.PENDING,
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
                OutboxEvent.status == OutboxStatus.PROCESSING,
                OutboxEvent.processing_started_at <= func.now() - processing_timeout,
            )
            .with_for_update(skip_locked=True)
            .limit(limit)
        )
        result: Result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def bulk_update_events_status(self, events: list[dict[str, str]]) -> None:
        table = OutboxEvent.__table__

        stmt = (
            update(table)
            .where(table.c.uuid == bindparam("event_uuid"))
            .values(
                status=bindparam("status"),
                retry_count=bindparam("retry_count"),
                next_retry_at=bindparam("next_retry_at"),
                processing_started_at=bindparam("processing_started_at"),
                attempt_id=bindparam("attempt_id"),
            )
        )

        await self.session.execute(stmt, events)

    async def bulk_update_processed_events_status(
        self, events: list[dict[str, str]]
    ) -> None:
        table = OutboxEvent.__table__
        stmt = (
            update(table)
            .where(
                table.c.uuid == bindparam("event_uuid"),
                table.c.attempt_id == bindparam("event_attempt_id"),
            )
            .values(
                status=bindparam("status"),
                retry_count=bindparam("retry_count"),
                next_retry_at=bindparam("next_retry_at"),
                processing_started_at=None,
            )
        )
        await self.session.execute(stmt, events)
