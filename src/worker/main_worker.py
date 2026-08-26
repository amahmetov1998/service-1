import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Callable

from src.clients import ServicePhoneClient
from src.config import ApplicationUnitOfWork, RetryBackoffStrategy
from src.exceptions import ServiceUnavailableError, AlreadyExistsError
from src.mappers import phone as phone_mapper, user as user_mapper
from src.models import User, PhoneSyncStatus
from src.schemas import UserSyncResult, IdempotencyHeaders

log = logging.getLogger(__name__)


class Worker:

    def __init__(
        self,
        service_phone_client: ServicePhoneClient,
        uow_factory: Callable[[], ApplicationUnitOfWork],
        retry_backoff_strategy: RetryBackoffStrategy,
        pending_users_per_worker: int,
        stuck_users_per_worker: int,
        max_concurrent_tasks: int,
        processing_timeout_seconds: int,
    ) -> None:
        self.client = service_phone_client
        self.uow_factory = uow_factory
        self.retry_backoff_strategy = retry_backoff_strategy
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self.pending_users_per_worker = pending_users_per_worker
        self.stuck_users_per_worker = stuck_users_per_worker
        self.processing_timeout = timedelta(seconds=processing_timeout_seconds)

    async def run(self) -> None:
        users = await self._get_users()
        if users:
            results = await asyncio.gather(*(self.sync_user(user) for user in users))

            await self._apply_sync_results(results=results)

    async def sync_user(self, user: User) -> UserSyncResult:
        service_payload = phone_mapper.orm_to_schemas(
            phones=user.phone_numbers,
        )
        headers = IdempotencyHeaders(idempotency_key=str(user.operation_id))
        async with self.semaphore:
            try:
                await self.client.send_phones(payload=service_payload, headers=headers)
                log.info(
                    "Phone data synchronized successfully for user uuid=%s",
                    user.uuid,
                )
                status = PhoneSyncStatus.DONE
                retry_count = 0
                next_retry_at = None

            except AlreadyExistsError as e:
                log.warning(
                    "Phone sync failed. user uuid=%s, error_type=%s, error=%s",
                    user.uuid,
                    type(e).__name__,
                    e,
                )
                status = None
                retry_count = 0
                next_retry_at = None

            except ServiceUnavailableError:
                if self.retry_backoff_strategy.can_retry(retry_count=user.retry_count):
                    backoff = self.retry_backoff_strategy.get_backoff(
                        retry_count=user.retry_count
                    )
                    status = PhoneSyncStatus.PENDING
                    retry_count = user.retry_count + 1
                    next_retry_at = datetime.now(timezone.utc) + backoff

                else:
                    status = PhoneSyncStatus.FAILED
                    retry_count = user.retry_count
                    next_retry_at = None

            except Exception as e:
                log.exception(
                    "Unexpected error while syncing user uuid=%s, error_type=%s, error=%s",
                    user.uuid,
                    type(e).__name__,
                    e,
                )
                status = PhoneSyncStatus.FAILED
                retry_count = user.retry_count
                next_retry_at = None

        return UserSyncResult(
            uuid=user.uuid,
            attempt_id=user.attempt_id,
            next_retry_at=next_retry_at,
            retry_count=retry_count,
            phone_sync_status=status,
        )

    async def _apply_sync_results(self, results: list[UserSyncResult]) -> None:
        deleted_user_data = [
            (result.uuid, result.attempt_id)
            for result in results
            if result.phone_sync_status is None
        ]

        processed_user_data = [
            result for result in results if result.phone_sync_status is not None
        ]
        users = user_mapper.schema_to_dict(results=processed_user_data)

        async with self.uow_factory() as uow:
            if deleted_user_data:
                await uow.users.soft_delete_users(deleted_user_data=deleted_user_data)
            if processed_user_data:
                await uow.users.update_users_status(users=users)

    async def _get_users(self) -> list[User]:
        async with self.uow_factory() as uow:
            pending_users = await uow.users.get_pending_users(
                limit=self.pending_users_per_worker
            )
            stuck_users = await uow.users.get_stuck_users(
                limit=self.stuck_users_per_worker,
                processing_timeout=self.processing_timeout,
            )
            processed = pending_users + stuck_users
            processed_users = user_mapper.orm_to_dict(
                users=processed, status=PhoneSyncStatus.PROCESSING
            )
            await uow.users.update_users_status(users=processed_users)

        return processed
