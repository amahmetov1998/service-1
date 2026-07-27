from uuid import UUID

from sqlalchemy import select, delete, update

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from sqlalchemy.orm import selectinload

from src.models import User, Phone
from src.schemas import UserCreateRequest, UserUpdateRequest, PhoneDetailAPIResponse


class UserRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def create_user_with_phones(
        self,
        payload: UserCreateRequest,
        phone_details_json: list[dict],
    ) -> User:
        user = User(
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email,
        )
        phone_details = [
            PhoneDetailAPIResponse.model_validate(item) for item in phone_details_json
        ]
        phone_details_map = {item.phone_number: item for item in phone_details}
        phones = []
        for phone in payload.phone_numbers:
            detail = phone_details_map.get(phone.phone_number)
            if detail:
                phones.append(
                    Phone(
                        phone_number=phone.phone_number,
                        phone_type=phone.phone_type,
                        is_verified=phone.is_verified,
                        operator_type=detail.operator_type,
                        region_type=detail.region_type,
                        is_spam=detail.is_spam,
                    )
                )

        user.phone_numbers = phones
        self.session.add(user)
        return user

    async def get_user_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result: Result = await self.session.execute(stmt)
        user: User | None = result.scalar_one_or_none()
        return user

    async def get_user_by_uuid(self, uuid: UUID) -> User | None:
        stmt = select(User).where(User.uuid == uuid)
        result: Result = await self.session.execute(stmt)
        user: User | None = result.scalar_one_or_none()
        return user

    async def get_user_with_phones(self, user_uuid: UUID) -> User | None:
        stmt = (
            select(User)
            .where(User.uuid == user_uuid)
            .options(selectinload(User.phone_numbers))
        )
        result: Result = await self.session.execute(stmt)
        user: User | None = result.scalar_one_or_none()
        return user

    async def delete_user(self, user_uuid: UUID) -> User | None:
        stmt = delete(User).where(User.uuid == user_uuid).returning(User)
        result: Result = await self.session.execute(stmt)
        user: User | None = result.scalar_one_or_none()
        return user

    async def update_user(
        self, user_uuid: UUID, payload: UserUpdateRequest
    ) -> User | None:
        values = payload.model_dump(exclude_unset=True)
        stmt = (
            update(User).where(User.uuid == user_uuid).values(**values).returning(User)
        )
        result: Result = await self.session.execute(stmt)
        user: User | None = result.scalar_one_or_none()
        return user
