import logging
from typing import Callable
from uuid import UUID

from src.clients import ServicePhoneClient
from src.config import RedisCache, ApplicationUnitOfWork
from src.exceptions import (
    NotFoundError,
    ValidationError,
    InvalidRequestError,
    AlreadyExistsError,
    USER_NOT_FOUND,
    USER_EXISTS,
    PHONE_DATA_EXISTS,
)
from src.exceptions import ServiceUnavailableError
from src.mappers import phone as phone_mapper, user as user_mapper
from src.models import User, Phone, PhoneSyncStatus
from src.schemas import (
    UserCreateRequest,
    UserUpdateRequest,
    UserPhonesResponse,
    PhoneCreateRequest,
)

log = logging.getLogger(__name__)


class UserService:
    def __init__(
        self,
        phone_client: ServicePhoneClient,
        uow_factory: Callable[[], ApplicationUnitOfWork],
        redis: RedisCache,
    ) -> None:
        self.uow_factory = uow_factory
        self.cache = redis
        self.client = phone_client

    async def create_user(
        self,
        payload: UserCreateRequest,
    ) -> UserPhonesResponse:
        user, phones = await self._create_user_with_phones(payload=payload)
        service_payload = phone_mapper.orm_to_schema(phones=phones)
        try:
            await self.client.send_phones(payload=service_payload)
            log.info(
                "Phone data synchronized successfully for user: uuid=%s",
                user.uuid,
            )
            status = PhoneSyncStatus.DONE

        except (
            InvalidRequestError,
            AlreadyExistsError,
            ValidationError,
        ) as e:
            log.warning(
                "Phone sync failed. Error type=%s, error=%s", type(e).__name__, e
            )
            status = PhoneSyncStatus.FAILED

        except ServiceUnavailableError:
            status = PhoneSyncStatus.PENDING

        status = await self._update_user_status(user_uuid=user.uuid, status=status)

        return user_mapper.orm_to_schema(user, phones, status)

    async def get_user(
        self,
        user_uuid: UUID,
    ) -> UserPhonesResponse:
        key = self.__get_user_cache_key(user_uuid=user_uuid)
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
        async with self.uow_factory() as uow:
            user = await uow.users.delete_user(user_uuid=user_uuid)
        if not user:
            raise NotFoundError(USER_NOT_FOUND)
        key = self.__get_user_cache_key(user_uuid=user_uuid)
        await self._invalidate_user_cache(key=key)

    async def update_user(
        self,
        user_uuid: UUID,
        payload: UserUpdateRequest,
    ) -> User:
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
            values = payload.model_dump(exclude_unset=True)
            user = await uow.users.update_user(user_uuid=user_uuid, values=values)
        if not user:
            raise NotFoundError(USER_NOT_FOUND)
        key = self.__get_user_cache_key(user_uuid=user_uuid)
        await self._invalidate_user_cache(key=key)
        return user

    async def _create_user_with_phones(
        self, payload: UserCreateRequest
    ) -> tuple[User, list[Phone]]:
        async with self.uow_factory() as uow:
            values = payload.model_dump(exclude={"phone_numbers"})
            user = await uow.users.create_user(values=values)
            if user is None:
                log.warning(
                    "User already exists with email=%s",
                    payload.email,
                )
                raise AlreadyExistsError(USER_EXISTS)
            phones_payload = phone_mapper.schema_to_dict(
                payload=payload, user_uuid=user.uuid
            )
            phones = await uow.phones.create_phones(
                phones_payload=phones_payload,
            )

            self._handle_existing_numbers(phones=phones, payload=payload.phone_numbers)

        log.info("User created successfully: uuid=%s", user.uuid)
        return user, phones

    async def _get_user(self, user_uuid: UUID) -> User:
        async with self.uow_factory() as uow:
            user = await uow.users.get_user_with_phones(user_uuid=user_uuid)
            if not user:
                log.warning("User does not exist with uuid=%s", user_uuid)
                raise NotFoundError(USER_NOT_FOUND)
            return user

    async def _update_user_status(
        self, user_uuid: UUID, status: PhoneSyncStatus | None
    ) -> PhoneSyncStatus:
        async with self.uow_factory() as uow:
            status = await uow.users.update_user_phone_status(
                user_uuid=user_uuid, status=status
            )
            return status

    async def _fetch_phones_detail(self, user: User) -> UserPhonesResponse:
        params = phone_mapper.orm_to_dict(user=user)

        try:
            phones = await self.client.get_phones(
                params=params,
            )
        except (
            InvalidRequestError,
            NotFoundError,
            ValidationError,
        ) as e:
            log.warning(
                "Phone sync failed. Error type=%s, error=%s", type(e).__name__, e
            )
            return UserPhonesResponse.model_validate(user)

        except ServiceUnavailableError:
            return UserPhonesResponse.model_validate(user)

        return user_mapper.dict_to_schema(phone_details=phones, user=user)

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

    @staticmethod
    def _handle_existing_numbers(
        phones: list[Phone], payload: list[PhoneCreateRequest]
    ) -> None:
        inserted = [phone.phone_number for phone in phones]
        incoming = [phone.phone_number for phone in payload]
        existing = list(set(incoming) - set(inserted))
        if existing:
            log.warning(
                "Phone(s) already exists with phone number(s)=%s",
                existing,
            )
            raise AlreadyExistsError(
                message=PHONE_DATA_EXISTS, details={"phone_numbers": existing}
            )

    @staticmethod
    def __get_user_cache_key(user_uuid: UUID) -> str:
        return f"user:{user_uuid}"
