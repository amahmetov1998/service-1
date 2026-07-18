import httpx

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import (
    UserNotFound,
    UserAlreadyExists,
)
from models import User
from schemas import (
    UserCreateRequest,
    UserUpdateRequest,
    UserPhonesResponse,
)
from src.repository import (
    users as user_repository,
)

from src import client
from utils import enrich_phone_numbers


async def create_user_with_phones(
    session: AsyncSession,
    user_payload: UserCreateRequest,
    http_client: httpx.AsyncClient,
) -> User:
    user: User | None = await user_repository.get_user_by_email(
        session, user_payload.email
    )
    if user:
        raise UserAlreadyExists()

    phone_details_json: list[dict] = await client.send_phone_detail(
        http_client, user_payload.phone_numbers
    )

    user: User = await user_repository.create_user_with_phones(
        session, user_payload, phone_details_json
    )

    await session.commit()

    return user


async def get_user_with_phones(
    session: AsyncSession,
    user_uuid: UUID,
    http_client: httpx.AsyncClient,
) -> UserPhonesResponse:
    user: User | None = await user_repository.get_user_with_phones(session, user_uuid)
    if not user:
        raise UserNotFound()

    phone_numbers = [phone.phone_number for phone in user.phone_numbers]

    phone_details_json: list[dict] = await client.get_phone_detail(
        http_client, phone_numbers
    )

    return enrich_phone_numbers(phone_details_json, user)


async def delete_user(
    session: AsyncSession,
    user_uuid: UUID,
) -> User:
    user: User | None = await user_repository.delete_user(session, user_uuid)
    if not user:
        raise UserNotFound()
    await session.commit()
    return user


async def update_user(
    session: AsyncSession,
    user_payload: UserUpdateRequest,
) -> User:
    user: User | None = await user_repository.update_user(session, user_payload)
    if not user:
        raise UserNotFound()
    await session.commit()
    return user
