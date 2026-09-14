from typing import Any

from sqlalchemy import Result, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Notification


class NotificationRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def create_notification(
        self,
        values: dict[str, Any],
    ) -> Notification:
        stmt = insert(Notification).values(**values).returning(Notification)
        result: Result = await self.session.execute(stmt)
        notification: Notification = result.scalar_one()

        return notification
