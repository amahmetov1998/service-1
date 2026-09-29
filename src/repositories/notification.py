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
        notification: Notification,
    ) -> Notification:
        self.session.add(notification)
        await self.session.flush()
        return notification
