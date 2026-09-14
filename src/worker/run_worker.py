import asyncio
import logging
import signal

import httpx

from src.clients import ServicePhoneClient
from src.config import (
    RetryBudgetStrategy,
    create_session_factory,
    settings,
    create_engine,
    configure_logging,
    RetryBackoffStrategy,
)
from src.dependencies import get_uow
from src.worker.main_worker import Worker

log = logging.getLogger(__name__)


async def run_worker():
    configure_logging(settings.logging)
    client = httpx.AsyncClient(
        base_url=settings.client.base_url,
        timeout=settings.client.timeout,
    )
    retry_budget_strategy = RetryBudgetStrategy(
        retry_cost=settings.retry.retry_cost,
        retry_budget_ratio=settings.retry.retry_budget_ratio,
        max_retry_budget=settings.retry.max_retry_budget,
    )
    retry_backoff_strategy = RetryBackoffStrategy(
        max_retry_count_per_entity=settings.worker.max_retry_count_per_user,
        max_backoff=settings.worker.max_backoff_minutes,
    )
    service_phone_client = ServicePhoneClient(
        client=client,
        retry_strategy=retry_budget_strategy,
    )
    engine = create_engine(settings.db.url)
    session_factory = create_session_factory(engine)
    uow_factory = get_uow(session_factory)
    worker = Worker(
        service_phone_client=service_phone_client,
        uow_factory=uow_factory,
        pending_users_per_worker=settings.worker.pending_users_per_worker,
        stuck_users_per_worker=settings.worker.stuck_users_per_worker,
        max_concurrent_tasks=settings.worker.max_concurrent_tasks,
        retry_backoff_strategy=retry_backoff_strategy,
        processing_timeout_seconds=settings.worker.processing_timeout_seconds,
    )

    stop_event = asyncio.Event()

    loop = asyncio.get_running_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    try:
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
                    timeout=settings.worker.poll_interval,
                )
            except asyncio.TimeoutError:
                pass

    finally:
        await engine.dispose()
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(run_worker())
