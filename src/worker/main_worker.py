from typing import Callable

import httpx

from src.clients import PhoneClient
from src.config import UnitOfWork
from src.exceptions import RetriesLimitError
from src.mappers import to_dict as mapping
from src.models import User


class Worker:
    def __init__(
        self,
        phone_client: PhoneClient,
        uow_factory: Callable[[], UnitOfWork],
    ):
        self.client = phone_client
        self.uow_factory = uow_factory

    async def run(self) -> None:
        async with self.uow_factory() as uow:

            users = await uow.users.get_pending_users()

        for user in users:
            await self.sync_user(user)

    async def sync_user(self, user: User) -> None:
        try:
            service_payload: list[dict] = mapping.phones_orm_to_dict(
                phones=user.phone_numbers,
            )
            await self.client.post(payload=service_payload)

            async with self.uow_factory() as uow:
                await uow.users.update_user_phone_status(
                    user_uuid=user.uuid,
                )

        except (
            httpx.TimeoutException,
            httpx.NetworkError,
            RetriesLimitError,
        ):
            pass
