import asyncio
import json
import logging
import signal

from aiokafka import AIOKafkaProducer

from dependencies import get_repository_factory, get_uow_factory
from src.broker import ServiceBroker
from src.config import (
    create_session_factory,
    settings,
    create_engine,
    configure_logging,
    RetryBackoffStrategy,
)
from src.workers.broker import BrokerWorker

log = logging.getLogger(__name__)


async def run_broker_worker():
    configure_logging(settings.logging)
    engine = create_engine(settings.db.url)
    session_factory = create_session_factory(engine)
    uow_factory = get_uow_factory(session_factory)
    repo_factory = get_repository_factory()
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.broker.url,
        acks=settings.broker.acks,
        enable_idempotence=settings.broker.enable_idempotence,
        value_serializer=lambda x: json.dumps(x).encode(),
        max_batch_size=settings.broker.max_batch_size,
        linger_ms=settings.broker.linger_ms,
    )
    retry_backoff_strategy = RetryBackoffStrategy(
        max_retry_count_per_entity=settings.broker.max_retry_count_per_entity,
        max_backoff=settings.broker.max_backoff_minutes,
    )
    service_broker = ServiceBroker(
        producer=producer,
    )
    worker = BrokerWorker(
        broker=service_broker,
        uow_factory=uow_factory,
        repo_factory=repo_factory,
        notification_topic_name=settings.broker.notification_topic_name,
        pending_tasks_per_publisher=settings.broker.pending_tasks_per_publisher,
        stuck_tasks_per_publisher=settings.broker.stuck_tasks_per_publisher,
        processing_timeout_seconds=settings.broker.processing_timeout_sec,
        retry_backoff_strategy=retry_backoff_strategy,
    )

    stop_event = asyncio.Event()

    loop = asyncio.get_running_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)
    try:
        await producer.start()

        while not stop_event.is_set():
            try:
                await worker.run()
            except Exception as e:
                log.exception(
                    "Unexpected error in worker. Error type=%s, error=%s",
                    type(e).__name__,
                    e,
                )
            try:
                await asyncio.wait_for(
                    stop_event.wait(),
                    timeout=settings.broker.poll_interval,
                )
            except asyncio.TimeoutError:
                pass

    finally:
        await producer.stop()


if __name__ == "__main__":
    asyncio.run(run_broker_worker())
