from datetime import timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import select, update, func, or_, tuple_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import User, PhoneSyncStatus


class UserRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def create_user(
        self,
        values: dict[str, Any],
    ) -> User | None:
        stmt = (
            insert(User)
            .values(**values)
            .on_conflict_do_nothing(index_elements=[User.email])
            .returning(User)
        )
        result: Result = await self.session.execute(stmt)
        user: User | None = result.scalar_one_or_none()

        return user

    async def get_user_by_email(
        self, email: str, exclude_user_uuid: UUID
    ) -> User | None:
        stmt = select(User).where(User.email == email, User.uuid != exclude_user_uuid)
        result: Result = await self.session.execute(stmt)
        user: User | None = result.scalar_one_or_none()
        return user

    async def get_user_with_phones(self, user_uuid: UUID) -> User | None:
        stmt = (
            select(User)
            .where(
                User.uuid == user_uuid,
                User.is_deleted.is_(False),
            )
            .options(selectinload(User.phone_numbers))
        )
        result: Result = await self.session.execute(stmt)
        user: User | None = result.scalar_one_or_none()
        return user

    async def get_user(self, user_uuid: UUID) -> User | None:
        stmt = select(User).where(
            User.uuid == user_uuid,
            User.is_deleted.is_(False),
        )
        result: Result = await self.session.execute(stmt)
        user: User | None = result.scalar_one_or_none()
        return user

    async def soft_delete_user(self, user_uuid: UUID) -> User | None:
        stmt = (
            update(User)
            .where(User.uuid == user_uuid)
            .values(is_deleted=True, phone_sync_status=None)
            .returning(User)
        )
        result: Result = await self.session.execute(stmt)
        user: User | None = result.scalar_one_or_none()
        return user

    async def update_user(self, user_uuid: UUID, values: dict[str, str]) -> User | None:
        stmt = (
            update(User)
            .where(User.uuid == user_uuid, User.is_deleted.is_(False))
            .values(**values)
            .returning(User)
        )
        result: Result = await self.session.execute(stmt)
        user: User | None = result.scalar_one_or_none()
        return user

    async def get_pending_users(self, limit: int) -> list[User]:
        stmt = (
            select(User)
            .where(
                User.phone_sync_status == PhoneSyncStatus.PENDING,
                User.is_deleted.is_(False),
                or_(User.next_retry_at.is_(None), User.next_retry_at <= func.now()),
            )
            .options(selectinload(User.phone_numbers))
            .with_for_update(skip_locked=True)
            .limit(limit)
        )
        result: Result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_stuck_users(
        self, limit: int, processing_timeout: timedelta
    ) -> list[User]:
        stmt = (
            select(User)
            .where(
                User.phone_sync_status == PhoneSyncStatus.PROCESSING,
                User.is_deleted.is_(False),
                User.processing_started_at <= func.now() - processing_timeout,
            )
            .options(selectinload(User.phone_numbers))
            .with_for_update(skip_locked=True)
            .limit(limit)
        )
        result: Result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_user_phone_status(
        self, user_uuid: UUID, status: PhoneSyncStatus
    ) -> None | User:
        stmt = (
            update(User)
            .where(User.uuid == user_uuid)
            .values(phone_sync_status=status)
            .returning(User)
        )

        result: Result = await self.session.execute(stmt)
        user: User | None = result.scalar_one_or_none()
        return user

    async def lock_email(self, email: str) -> None:
        await self.session.execute(
            select(
                func.pg_advisory_xact_lock(
                    func.hashtextextended(email.lower(), 0),
                ),
            )
        )

    async def update_processed_users_status(self, users: list[dict[str, str]]) -> None:
        for user in users:
            stmt = (
                update(User)
                .where(
                    User.uuid == user["uuid"],
                    User.attempt_id == user["attempt_id"],
                )
                .values(
                    phone_sync_status=user["phone_sync_status"],
                    retry_count=user["retry_count"],
                    next_retry_at=user["next_retry_at"],
                    processing_started_at=None,
                )
            )
            await self.session.execute(stmt)

    async def update_users_status(self, users: list[dict[str, str]]) -> None:
        for user in users:
            stmt = (
                update(User)
                .where(User.uuid == user["uuid"])
                .values(
                    phone_sync_status=user["phone_sync_status"],
                    retry_count=user["retry_count"],
                    next_retry_at=user["next_retry_at"],
                    processing_started_at=user["processing_started_at"],
                )
            )
            await self.session.execute(stmt)

    async def soft_delete_users(
        self, deleted_user_data: list[tuple[UUID, UUID]]
    ) -> None:
        stmt = (
            update(User)
            .where(tuple_(User.uuid, User.attempt_id).in_(deleted_user_data))
            .values(is_deleted=True, phone_sync_status=None)
        )
        await self.session.execute(stmt)
