import logging
from typing import Callable
from uuid import UUID

import httpx

from src import mappers as mapping
from src.clients import PhoneClient
from src.config import RedisCache, UnitOfWork
from src.enums import PhoneSyncStatus
from src.exceptions import (
    RetriesLimitError,
    NotFoundError,
    ValidationError,
    InvalidRequestError,
    AlreadyExistsError,
    USER_NOT_FOUND,
    USER_EXISTS,
    PHONE_DATA_ALREADY_EXISTS,
)
from src.models import User, Phone
from src.schemas import (
    UserCreateRequest,
    UserUpdateRequest,
    UserPhonesResponse,
)
from src.utils import get_user_cache_key

log = logging.getLogger(__name__)


class UserService:
    def __init__(
        self,
        phone_client: PhoneClient,
        uow_factory: Callable[[], UnitOfWork],
        redis: RedisCache,
    ) -> None:
        self.uow_factory = uow_factory
        self.cache = redis
        self.client = phone_client

    async def create_user(
        self,
        payload: UserCreateRequest,
    ) -> UserPhonesResponse:
        user, phones = await self._create_user_with_phones(
            payload=payload,
            status=PhoneSyncStatus.PENDING,
        )

        synced = await self._sync_phones(payload=phones)
        if synced:
            log.info(
                "Phone data synchronized successfully for user: uuid=%s",
                user.uuid,
            )
            status = await self._update_user_status(user_uuid=user.uuid)
        else:
            status = PhoneSyncStatus.PENDING
        return mapping.user_phones_to_schema(user, phones, status)

    async def get_user(
        self,
        user_uuid: UUID,
    ) -> UserPhonesResponse:
        key = get_user_cache_key(user_uuid=user_uuid)
        cached_user = await self._get_cached_user(key=key)
        if cached_user:
            return cached_user

        user = await self._get_user(user_uuid=user_uuid)

        user_with_phones = await self._fetch_phones_detail(user=user)
        await self._cache_user(key=key, user_with_phones=user_with_phones)
        return user_with_phones

    async def delete_user(
        self,
        user_uuid: UUID,
    ) -> None:

        key = get_user_cache_key(user_uuid=user_uuid)
        await self._invalidate_user_cache(key=key)

        async with self.uow_factory() as uow:
            user = await uow.users.delete_user(user_uuid=user_uuid)
        if not user:
            raise NotFoundError(USER_NOT_FOUND)

    async def update_user(
        self,
        user_uuid: UUID,
        payload: UserUpdateRequest,
    ) -> User:
        key = get_user_cache_key(user_uuid=user_uuid)
        await self._invalidate_user_cache(key)
        async with self.uow_factory() as uow:
            if payload.email:
                await uow.users.lock_email(email=payload.email)
                user_exists = await uow.users.get_user_by_email(email=payload.email)
                if user_exists:
                    log.warning(
                        "User already exists with email=%s",
                        payload.email,
                    )
                    raise AlreadyExistsError(USER_EXISTS)

            user = await uow.users.update_user(user_uuid, payload=payload)
        if not user:
            raise NotFoundError(USER_NOT_FOUND)
        return user

    async def _create_user_with_phones(
        self, payload: UserCreateRequest, status: PhoneSyncStatus
    ) -> tuple[User, list[Phone]]:
        async with self.uow_factory() as uow:
            user = await uow.users.create_user(
                payload=payload,
                phone_sync_status=status,
            )
            if user is None:
                log.warning(
                    "User already exists with email=%s",
                    payload.email,
                )
                raise AlreadyExistsError(USER_EXISTS)
            phones = await uow.users.create_phones(
                payload=payload,
                user_uuid=user.uuid,
            )

            if len(phones) != len(payload.phone_numbers):
                log.warning(
                    "Phone(s) already exists with phone number(s)=%s",
                    payload.phone_numbers,
                )
                raise AlreadyExistsError(PHONE_DATA_ALREADY_EXISTS)
        log.info("User created successfully: uuid=%s", user.uuid)
        return user, phones

    async def _get_user(self, user_uuid: UUID) -> User:
        async with self.uow_factory() as uow:
            user = await uow.users.get_user_with_phones(user_uuid=user_uuid)
            if not user:
                log.warning("User does not exist with uuid=%s", user_uuid)
                raise NotFoundError(USER_NOT_FOUND)
            return user

    async def _sync_phones(self, payload: list[Phone]) -> bool:
        service_payload = mapping.phones_orm_to_dict(phones=payload)
        try:
            await self.client.post(payload=service_payload)
            return True

        except (
            httpx.TimeoutException,
            httpx.NetworkError,
        ) as e:
            log.warning("Service not available: %s", e)
            return False
        except (
            RetriesLimitError,
            InvalidRequestError,
            AlreadyExistsError,
            ValidationError,
        ):
            return False

    async def _update_user_status(self, user_uuid: UUID) -> PhoneSyncStatus:
        async with self.uow_factory() as uow:
            status = await uow.users.update_user_phone_status(user_uuid=user_uuid)
            return status

    async def _fetch_phones_detail(self, user: User) -> UserPhonesResponse:
        params = mapping.phones_orm_to_list(user=user)

        try:
            response = await self.client.get(
                params=params,
            )
            phone_details_json = response.json()
            user_with_phones = mapping.response_to_schema(phone_details_json, user)
            return user_with_phones
        except (
            httpx.TimeoutException,
            httpx.NetworkError,
        ) as e:
            log.warning("Service not available: %s", e)
            return UserPhonesResponse.model_validate(user)

        except (
            InvalidRequestError,
            NotFoundError,
            RetriesLimitError,
            ValidationError,
        ):
            return UserPhonesResponse.model_validate(user)

    async def _get_cached_user(self, key: str) -> UserPhonesResponse | None:
        cached = await self.cache.get(key)
        if cached:
            return UserPhonesResponse.model_validate(cached)

        return None

    async def _cache_user(self, key: str, user_with_phones: UserPhonesResponse) -> None:
        user_for_cache = user_with_phones.model_dump(mode="json")
        await self.cache.set(key, user_for_cache)

    async def _invalidate_user_cache(self, key: str) -> None:
        await self.cache.delete(key)
