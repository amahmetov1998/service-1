import asyncio
import logging
from datetime import timedelta, datetime, timezone
from typing import Callable

from aiokafka import AIOKafkaProducer
from aiokafka.errors import (
    KafkaConnectionError,
    KafkaTimeoutError,
    RequestTimedOutError,
)

from src.config import ApplicationUnitOfWork, RetryBackoffStrategy
from src.mappers import outbox_event as outbox_event_mapper
from src.models import OutboxEvent, TaskStatus
from src.schemas import OutboxEventSchema, IdempotencyHeaders, SentNotificationResult

log = logging.getLogger(__name__)


class OutboxPublisher:

    def __init__(
        self,
        producer: AIOKafkaProducer,
        uow_factory: Callable[[], ApplicationUnitOfWork],
        retry_backoff_strategy: RetryBackoffStrategy,
        notification_topic_name: str,
        pending_tasks_per_publisher: int,
        stuck_tasks_per_publisher: int,
        processing_timeout_seconds: int,
    ):
        self.producer = producer
        self.uow_factory = uow_factory
        self.notification_topic_name = notification_topic_name
        self.pending_tasks_per_publisher = pending_tasks_per_publisher
        self.stuck_tasks_per_publisher = stuck_tasks_per_publisher
        self.processing_timeout = timedelta(seconds=processing_timeout_seconds)
        self.retry_backoff_strategy = retry_backoff_strategy

    async def run(self) -> None:
        events = await self._get_events()
        if events:
            results = await asyncio.gather(
                *(self._publish_message(event) for event in events)
            )

            await self._apply_sent_results(results=results)

    async def _publish_message(self, event: OutboxEvent):
        payload = OutboxEventSchema.model_validate(event).model_dump(mode="json")
        headers_schema = IdempotencyHeaders(idempotency_key=str(event.message_id))
        headers = [("Idempotency-Key", headers_schema.idempotency_key.encode())]
        try:
            await self.producer.send_and_wait(
                headers=headers,
                topic=self.notification_topic_name,
                value=payload,
            )
            status = TaskStatus.SENT
            retry_count = 0
            next_retry_at = None
        except (KafkaConnectionError, KafkaTimeoutError, RequestTimedOutError):
            if self.retry_backoff_strategy.can_retry(retry_count=event.retry_count):
                backoff = self.retry_backoff_strategy.get_backoff(
                    retry_count=event.retry_count
                )
                status = TaskStatus.PENDING
                retry_count = event.retry_count + 1
                next_retry_at = datetime.now(timezone.utc) + backoff
            else:
                status = TaskStatus.FAILED
                retry_count = event.retry_count
                next_retry_at = None
        except Exception as e:
            log.exception(
                "Unexpected broker error while sending notification uuid=%s, error_type=%s, error=%s",
                event.uuid,
                type(e).__name__,
                e,
            )
            status = TaskStatus.FAILED
            retry_count = event.retry_count
            next_retry_at = None
        return SentNotificationResult(
            uuid=event.uuid,
            attempt_id=event.attempt_id,
            next_retry_at=next_retry_at,
            retry_count=retry_count,
            status=status,
        )

    async def _get_events(self):
        async with self.uow_factory() as uow:
            pending = await uow.events.get_pending(
                limit=self.pending_tasks_per_publisher
            )
            stuck = await uow.events.get_stuck(
                limit=self.stuck_tasks_per_publisher,
                processing_timeout=self.processing_timeout,
            )
            processed = pending + stuck
            processed_events = outbox_event_mapper.orm_to_dict(
                events=processed, status=TaskStatus.PROCESSING
            )
            await uow.events.update_events_status(events=processed_events)
        return processed

    async def _apply_sent_results(self, results: list[SentNotificationResult]) -> None:
        events = outbox_event_mapper.schema_to_dict(results=results)

        async with self.uow_factory() as uow:
            if events:
                await uow.events.update_processed_events_status(events=events)
