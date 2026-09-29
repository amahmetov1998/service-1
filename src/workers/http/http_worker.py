import asyncio
import logging
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from typing import Callable

from src.clients import ServicePhoneClient
from src.config import (
    UnitOfWork,
    RetryBackoffStrategy,
    HTTPWorkerContext,
    RepositoryFactory,
)
from src.exceptions import (
    ServiceUnavailableError,
    AlreadyExistsError,
    IdempotencyConflictError,
)
from src.mappers import phone as phone_mapper, user as user_mapper
from src.models import User, PhoneSyncStatus
from src.schemas import UserSyncResult, IdempotencyHeaders

log = logging.getLogger(__name__)


class HTTPWorker:

    def __init__(
        self,
        service_phone_client: ServicePhoneClient,
        uow_factory: Callable[[], UnitOfWork],
        repo_factory: RepositoryFactory,
        retry_backoff_strategy: RetryBackoffStrategy,
        pending_users_per_worker: int,
        stuck_users_per_worker: int,
        max_concurrent_tasks: int,
        processing_timeout_seconds: int,
    ) -> None:
        self.client = service_phone_client
        self.uow_factory = uow_factory
        self.repo_factory = repo_factory
        self.retry_backoff_strategy = retry_backoff_strategy
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self.pending_users_per_worker = pending_users_per_worker
        self.stuck_users_per_worker = stuck_users_per_worker
        self.processing_timeout = timedelta(seconds=processing_timeout_seconds)

    @asynccontextmanager
    async def _ctx(self):
        async with self.uow_factory() as uow:
            yield HTTPWorkerContext(uow=uow, repo_factory=self.repo_factory)

    async def run(self) -> None:
        users = await self._get_users()
        if users:
            results = await asyncio.gather(*(self.sync_user(user) for user in users))

            await self._apply_sync_results(results=results)

    async def sync_user(self, user: User) -> UserSyncResult:
        try:
            service_payload = phone_mapper.orm_to_schemas(
                phones=user.phone_numbers,
            )
            headers = IdempotencyHeaders(idempotency_key=str(user.operation_id))
            async with self.semaphore:
                await self.client.send_phones(payload=service_payload, headers=headers)
                log.info(
                    "Phone data synchronized successfully for user uuid=%s",
                    user.uuid,
                )
                return UserSyncResult(
                    uuid=user.uuid,
                    attempt_id=user.attempt_id,
                    next_retry_at=None,
                    retry_count=0,
                    phone_sync_status=PhoneSyncStatus.DONE,
                )

        except AlreadyExistsError as e:
            log.warning(
                "Phone data synchronized failed. user uuid=%s, error_type=%s, error=%s",
                user.uuid,
                type(e).__name__,
                e,
            )
            return UserSyncResult(
                uuid=user.uuid,
                attempt_id=user.attempt_id,
                next_retry_at=None,
                retry_count=0,
                phone_sync_status=None,
            )
        except IdempotencyConflictError as e:
            log.warning(
                "Phone data synchronized failed. Error type=%s, error=%s",
                type(e).__name__,
                e,
            )
            return UserSyncResult(
                uuid=user.uuid,
                attempt_id=user.attempt_id,
                next_retry_at=None,
                retry_count=user.retry_count,
                phone_sync_status=PhoneSyncStatus.FAILED,
            )
        except ServiceUnavailableError:
            return self._get_retry_result(user=user)
        except Exception as e:
            log.exception(
                "Unexpected error while sending data to service. Error type=%s, error=%s",
                type(e).__name__,
                e,
            )
            return self._get_retry_result(user=user)

    async def _apply_sync_results(self, results: list[UserSyncResult]) -> None:
        deleted_user_data = [
            (result.uuid, result.attempt_id)
            for result in results
            if result.phone_sync_status is None
        ]

        processed_user_data = [
            result for result in results if result.phone_sync_status is not None
        ]
        users = user_mapper.schema_to_orm(results=processed_user_data)

        async with self._ctx() as ctx:
            if deleted_user_data:
                await ctx.users.soft_delete_users(deleted_user_data=deleted_user_data)
            if processed_user_data:
                await ctx.users.update_processed_users_status(users=users)

    async def _get_users(self) -> list[User]:
        async with self._ctx() as ctx:
            pending_users = await ctx.users.get_pending_users(
                limit=self.pending_users_per_worker
            )
            stuck_users = await ctx.users.get_stuck_users(
                limit=self.stuck_users_per_worker,
                processing_timeout=self.processing_timeout,
            )
            users = pending_users + stuck_users
            await self._update_user_fields(users=users)
            await ctx.users.update_users_status(
                users=users, status=PhoneSyncStatus.PROCESSING
            )
        return users

    async def _update_user_fields(self, users: list[User]) -> None:
        for user in users:
            user.attempt_id = uuid.uuid4()
            user.processing_started_at = datetime.now(timezone.utc)

    def _get_retry_result(self, user: User) -> UserSyncResult:
        if self.retry_backoff_strategy.can_retry(retry_count=user.retry_count):
            backoff = self.retry_backoff_strategy.get_backoff(
                retry_count=user.retry_count
            )

            return UserSyncResult(
                uuid=user.uuid,
                attempt_id=user.attempt_id,
                phone_sync_status=PhoneSyncStatus.PENDING,
                retry_count=user.retry_count + 1,
                next_retry_at=datetime.now(timezone.utc) + backoff,
            )

        return UserSyncResult(
            uuid=user.uuid,
            attempt_id=user.attempt_id,
            next_retry_at=None,
            retry_count=user.retry_count,
            phone_sync_status=PhoneSyncStatus.FAILED,
        )
