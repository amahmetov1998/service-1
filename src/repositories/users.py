from uuid import UUID

from pydantic import EmailStr
from sqlalchemy import select, update, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src import mappers as mapping
from src.enums import PhoneSyncStatus
from src.models import User, Phone
from src.schemas import UserCreateRequest, UserUpdateRequest


class UserRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def create_user(
        self,
        payload: UserCreateRequest,
        phone_sync_status: PhoneSyncStatus,
    ) -> User | None:
        stmt = (
            insert(User)
            .values(
                first_name=payload.first_name,
                last_name=payload.last_name,
                phone_sync_status=phone_sync_status,
                email=payload.email,
            )
            .on_conflict_do_nothing(index_elements=[User.email])
            .returning(User)
        )
        result: Result = await self.session.execute(stmt)
        user: User | None = result.scalar_one_or_none()

        return user

    async def get_user_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
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
        stmt = (
            update(User)
            .where(User.uuid == user_uuid)
            .values(
                is_deleted=True,
                updated_at=func.now(),
            )
            .returning(User)
        )
        result: Result = await self.session.execute(stmt)
        user: User | None = result.scalar_one_or_none()
        return user

    async def update_user(
        self, user_uuid: UUID, payload: UserUpdateRequest
    ) -> User | None:
        values = payload.model_dump(exclude_unset=True)
        stmt = (
            update(User)
            .where(User.uuid == user_uuid)
            .values(
                **values,
                updated_at=func.now(),
            )
            .returning(User)
        )
        result: Result = await self.session.execute(stmt)
        user: User | None = result.scalar_one_or_none()
        return user

    async def get_pending_users(self) -> list[User]:
        stmt = (
            select(User)
            .where(User.phone_sync_status == PhoneSyncStatus.PENDING)
            .options(selectinload(User.phone_numbers))
        )
        result: Result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_user_phone_status(self, user_uuid: UUID) -> PhoneSyncStatus:
        stmt = (
            update(User)
            .where(User.uuid == user_uuid)
            .values(phone_sync_status=PhoneSyncStatus.DONE)
            .returning(User.phone_sync_status)
        )

        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def create_phones(
        self, payload: UserCreateRequest, user_uuid: UUID
    ) -> list[Phone]:
        phones_payload = mapping.phones_schema_to_dict(
            payload=payload, user_uuid=user_uuid
        )
        result = await self.session.execute(
            insert(Phone)
            .on_conflict_do_nothing(index_elements=[Phone.phone_number])
            .returning(Phone),
            phones_payload,
        )
        return list(result.scalars().all())

    async def lock_email(self, email: EmailStr) -> None:
        await self.session.execute(
            select(
                func.pg_advisory_xact_lock(
                    func.hashtextextended(email.lower(), 0),
                ),
            )
        )
