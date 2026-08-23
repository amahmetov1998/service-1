import asyncio
import logging
from datetime import datetime, timezone
from typing import Callable

from src.clients import ServicePhoneClient
from src.config import ApplicationUnitOfWork, RetryBackoffStrategy
from src.exceptions import ServiceUnavailableError, AlreadyExistsError
from src.mappers import phone as phone_mapper, user as user_mapper
from src.models import User, PhoneSyncStatus
from src.schemas import UserSyncResult

log = logging.getLogger(__name__)


class Worker:
    def __init__(
        self,
        service_phone_client: ServicePhoneClient,
        uow_factory: Callable[[], ApplicationUnitOfWork],
        retry_backoff_strategy: RetryBackoffStrategy,
        users_per_worker: int,
        max_concurrent_tasks: int,
    ) -> None:
        self.client = service_phone_client
        self.uow_factory = uow_factory
        self.retry_backoff_strategy = retry_backoff_strategy
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self.users_per_worker = users_per_worker

    async def run(self) -> None:
        users = await self._get_pending_users()

        results = await asyncio.gather(*(self.sync_user(user) for user in users))

        await self._apply_sync_results(results=results)

    async def sync_user(self, user: User) -> UserSyncResult:
        service_payload = phone_mapper.orm_to_schema(
            phones=user.phone_numbers,
        )
        async with self.semaphore:
            try:
                await self.client.send_phones(payload=service_payload)
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
            next_retry_at=next_retry_at,
            retry_count=retry_count,
            phone_sync_status=status,
        )

    async def _apply_sync_results(self, results: list[UserSyncResult]) -> None:
        delete_user_uuids = [
            result.uuid for result in results if result.phone_sync_status is None
        ]

        processed_users = [
            result for result in results if result.phone_sync_status is not None
        ]
        users = user_mapper.schema_to_dict(results=processed_users)

        async with self.uow_factory() as uow:
            if delete_user_uuids:
                await uow.users.soft_delete_users(user_uuids=delete_user_uuids)
            if processed_users:
                await uow.users.update_users_status(users=users)

    async def _get_pending_users(self) -> list[User]:
        async with self.uow_factory() as uow:
            users_orm = await uow.users.get_pending_users(limit=self.users_per_worker)
            users = user_mapper.orm_to_dict(
                users=users_orm, status=PhoneSyncStatus.PROCESSING
            )
            await uow.users.update_users_status(users=users)
        return users_orm
