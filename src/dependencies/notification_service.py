from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.services import NotificationService
from .session import get_session
from .uow import get_repository_factory


def get_notification_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> NotificationService:
    repo_factory = get_repository_factory()
    events = repo_factory.outbox_event(session)
    notifications = repo_factory.notification(session)
    users = repo_factory.user(session)
    return NotificationService(
        users=users,
        events=events,
        notifications=notifications,
    )
