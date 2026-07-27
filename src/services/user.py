from uuid import UUID

from src.cache import RedisCache
from src.clients.client import PhoneClient
from src.core.exceptions import (
    UserNotFoundError,
    UserAlreadyExistsError,
)
from src.models import User
from src.repositories import UserRepository
from src.schemas import (
    UserCreateRequest,
    UserUpdateRequest,
    UserPhonesResponse,
)

from src.utils import enrich_phone_numbers


class UserService:
    def __init__(
        self,
        phone_client: PhoneClient,
        user_repository: UserRepository,
        redis: RedisCache,
    ) -> None:
        self.user_repository = user_repository
        self.cache = redis
        self.client = phone_client

    async def create_user_with_phones(
        self,
        payload: UserCreateRequest,
    ) -> User:

        user: User | None = await self.user_repository.get_user_by_email(
            email=payload.email
        )
        if user:
            raise UserAlreadyExistsError()
        phone_details_json: list[dict] = await self.client.send_phone_detail(
            phone_list=payload.phone_numbers,
        )

        user: User = await self.user_repository.create_user_with_phones(
            payload=payload, phone_details_json=phone_details_json
        )

        await self.user_repository.session.commit()

        return user

    async def get_user_with_phones(
        self,
        user_uuid: UUID,
    ) -> UserPhonesResponse:
        key = f"user_{user_uuid}"
        cached_user = await self.cache.get(key)
        if cached_user:
            return UserPhonesResponse.model_validate(cached_user)

        user: User | None = await self.user_repository.get_user_with_phones(
            user_uuid=user_uuid
        )
        if not user:
            raise UserNotFoundError()

        phone_numbers = [phone.phone_number for phone in user.phone_numbers]

        phone_details_json: list[dict] = await self.client.get_phone_detail(
            phone_numbers=phone_numbers,
        )

        user_with_phones: UserPhonesResponse = enrich_phone_numbers(
            phone_details_json, user
        )
        user_for_cache: dict = user_with_phones.model_dump(mode="json")
        await self.cache.set(key, user_for_cache)

        return user_with_phones

    async def delete_user(
        self,
        user_uuid: UUID,
    ) -> None:
        key = f"user_{user_uuid}"
        await self.cache.delete(key)
        user: User | None = await self.user_repository.delete_user(user_uuid=user_uuid)
        if not user:
            raise UserNotFoundError()
        await self.user_repository.session.commit()

    async def update_user(
        self,
        user_uuid: UUID,
        payload: UserUpdateRequest,
    ) -> User:
        key = f"user_{user_uuid}"
        await self.cache.delete(key)
        user: User | None = await self.user_repository.update_user(
            user_uuid, payload=payload
        )
        if not user:
            raise UserNotFoundError()
        await self.user_repository.session.commit()
        return user
