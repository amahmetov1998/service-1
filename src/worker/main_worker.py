import asyncio
import logging
from typing import Callable

from src.clients import ServicePhoneClient
from src.config import ApplicationUnitOfWork
from src.exceptions import (
    ServiceUnavailableError,
    InvalidRequestError,
    AlreadyExistsError,
    ValidationError,
)
from src.mappers import phone as phone_mapper, user as user_mapper
from src.models import User, PhoneSyncStatus
from src.schemas import UserSyncResult

log = logging.getLogger(__name__)


class Worker:
    def __init__(
        self,
        service_phone_client: ServicePhoneClient,
        uow_factory: Callable[[], ApplicationUnitOfWork],
    ) -> None:
        self.client = service_phone_client
        self.uow_factory = uow_factory
        self.semaphore = asyncio.Semaphore(5)

    async def run(self) -> None:
        async with self.uow_factory() as uow:

            users = await uow.users.get_pending_users()
            users_dict = user_mapper.orm_to_dict(users=users)
            await uow.users.update_users_phone_status(users_dict=users_dict)

        results = await asyncio.gather(
            *(self.sync_user(user) for user in users), return_exceptions=True
        )
        sync_results = []
        for result in results:
            if isinstance(result, Exception):
                continue
            sync_results.append(result)
        users_dict = user_mapper.schema_to_dict(sync_results=sync_results)
        async with self.uow_factory() as uow:
            await uow.users.update_users_phone_status(users_dict=users_dict)

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

            except (
                InvalidRequestError,
                AlreadyExistsError,
                ValidationError,
            ) as e:
                log.warning(
                    "Phone sync failed. user uuid=%s, error_type=%s, error=%s",
                    user.uuid,
                    type(e).__name__,
                    e,
                )
                status = PhoneSyncStatus.FAILED

            except ServiceUnavailableError:
                status = PhoneSyncStatus.PENDING

            except Exception as e:
                log.exception(
                    "Unexpected error while syncing user uuid=%s, error_type=%s, error=%s",
                    user.uuid,
                    type(e).__name__,
                    e,
                )
                raise

        return UserSyncResult(
            uuid=user.uuid,
            phone_sync_status=status,
        )
