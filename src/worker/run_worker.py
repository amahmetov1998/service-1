import asyncio
import signal

from src.providers import (
    create_work_dependencies,
    create_phone_client,
    create_uow_factory,
)
from src.worker.main_worker import Worker


async def run_worker():
    deps = create_work_dependencies()

    phone_client = create_phone_client(deps)
    uow_factory = create_uow_factory(deps)

    worker = Worker(
        phone_client=phone_client,
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
        await deps.engine.dispose()
        await deps.http_client.aclose()


if __name__ == "__main__":
    asyncio.run(run_worker())
