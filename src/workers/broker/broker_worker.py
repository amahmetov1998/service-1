import asyncio
import logging
import uuid
from contextlib import asynccontextmanager
from datetime import timedelta, datetime, timezone
from typing import Callable

from src.broker import ServiceBroker
from src.config import (
    UnitOfWork,
    RetryBackoffStrategy,
    BrokerWorkerContext,
    RepositoryFactory,
)
from src.exceptions import BrokerUnavailableError
from src.mappers import outbox_event as outbox_event_mapper
from src.models import OutboxEvent, OutboxStatus
from src.schemas import OutboxEventSchema, IdempotencyHeaders, SentNotificationResult

log = logging.getLogger(__name__)


class BrokerWorker:

    def __init__(
        self,
        broker: ServiceBroker,
        uow_factory: Callable[[], UnitOfWork],
        repo_factory: RepositoryFactory,
        retry_backoff_strategy: RetryBackoffStrategy,
        notification_topic_name: str,
        pending_tasks_per_publisher: int,
        stuck_tasks_per_publisher: int,
        processing_timeout_seconds: int,
    ):
        self.broker = broker
        self.uow_factory = uow_factory
        self.repo_factory = repo_factory
        self.notification_topic_name = notification_topic_name
        self.pending_tasks_per_publisher = pending_tasks_per_publisher
        self.stuck_tasks_per_publisher = stuck_tasks_per_publisher
        self.processing_timeout = timedelta(seconds=processing_timeout_seconds)
        self.retry_backoff_strategy = retry_backoff_strategy

    @asynccontextmanager
    async def _ctx(self):
        async with self.uow_factory() as uow:
            yield BrokerWorkerContext(uow=uow, repo_factory=self.repo_factory)

    async def run(self) -> None:
        events = await self._get_events()
        if not events:
            return
        results = await asyncio.gather(
            *(self._publish_message(event) for event in events),
        )

        await self._apply_sent_results(results=results)

    async def _publish_message(self, event: OutboxEvent) -> SentNotificationResult:
        try:
            payload = OutboxEventSchema.model_validate(event.payload)
            headers = IdempotencyHeaders(idempotency_key=str(event.message_id))
            await self.broker.send_and_wait_ack(
                headers=headers,
                topic_name=self.notification_topic_name,
                event=payload,
            )
            return SentNotificationResult(
                uuid=event.uuid,
                attempt_id=event.attempt_id,
                next_retry_at=None,
                retry_count=0,
                status=OutboxStatus.SENT,
            )
        except BrokerUnavailableError:
            return self._get_retry_result(event)
        except Exception as e:
            log.exception(
                "Unexpected error while sending event to broker. Error type=%s, error=%s",
                type(e).__name__,
                e,
            )
            return self._get_retry_result(event)

    async def _get_events(self):
        async with self._ctx() as ctx:
            pending = await ctx.events.get_pending(
                limit=self.pending_tasks_per_publisher
            )
            stuck = await ctx.events.get_stuck(
                limit=self.stuck_tasks_per_publisher,
                processing_timeout=self.processing_timeout,
            )
            events = pending + stuck
            if events:
                await self._update_event_fields(events=events)
                processed_events = outbox_event_mapper.orm_to_dicts(
                    events=events, status=OutboxStatus.PROCESSING
                )
                await ctx.events.bulk_update_events_status(events=processed_events)
        return events

    async def _update_event_fields(self, events: list[OutboxEvent]) -> None:
        for event in events:
            event.attempt_id = uuid.uuid4()
            event.processing_started_at = datetime.now(timezone.utc)

    async def _apply_sent_results(self, results: list[SentNotificationResult]) -> None:
        events = outbox_event_mapper.schema_to_dicts(results=results)

        async with self._ctx() as ctx:
            await ctx.events.bulk_update_processed_events_status(events=events)

    def _get_retry_result(
        self,
        event: OutboxEvent,
    ) -> SentNotificationResult:
        if self.retry_backoff_strategy.can_retry(retry_count=event.retry_count):
            backoff = self.retry_backoff_strategy.get_backoff(
                retry_count=event.retry_count
            )

            return SentNotificationResult(
                uuid=event.uuid,
                attempt_id=event.attempt_id,
                status=OutboxStatus.PENDING,
                retry_count=event.retry_count + 1,
                next_retry_at=datetime.now(timezone.utc) + backoff,
            )

        return SentNotificationResult(
            uuid=event.uuid,
            attempt_id=event.attempt_id,
            status=OutboxStatus.FAILED,
            retry_count=event.retry_count,
            next_retry_at=None,
        )
