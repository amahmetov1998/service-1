import asyncio
import signal

import httpx

from src.clients import ServicePhoneClient
from src.config import (
    RetryBudgetStrategy,
    create_session_factory,
    settings,
    create_engine,
    configure_logging,
)
from src.dependencies import get_uow
from src.worker.main_worker import Worker


async def run_worker():
    configure_logging(settings.logging)
    client = httpx.AsyncClient(
        base_url=settings.client.base_url,
        timeout=settings.client.timeout,
    )
    retry_strategy = RetryBudgetStrategy(
        retry_cost=settings.retry.retry_cost,
        retry_budget_ratio=settings.retry.retry_budget_ratio,
        max_retry_budget=settings.retry.max_retry_budget,
    )
    service_phone_client = ServicePhoneClient(
        client=client,
        retry_strategy=retry_strategy,
    )
    engine = create_engine(settings.db.url)
    session_factory = create_session_factory(engine)
    uow_factory = get_uow(session_factory)
    worker = Worker(
        service_phone_client=service_phone_client,
        uow_factory=uow_factory,
    )

    stop_event = asyncio.Event()

    loop = asyncio.get_running_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    try:
        while not stop_event.is_set():
            await worker.run()

            try:
                await asyncio.wait_for(
                    stop_event.wait(),
                    timeout=10,
                )
            except asyncio.TimeoutError:
                pass

    finally:
        await engine.dispose()
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(run_worker())
