from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.services import NotificationService
from .session_factory import get_session_factory
from .uow import get_repository_factory, get_uow_factory


def get_notification_service(
    session_factory: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_session_factory)
    ],
) -> NotificationService:
    uow_factory = get_uow_factory(session_factory=session_factory)
    repo_factory = get_repository_factory()
    return NotificationService(
        uow_factory=uow_factory,
        repo_factory=repo_factory,
    )
