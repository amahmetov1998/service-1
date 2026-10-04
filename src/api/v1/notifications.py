from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.dependencies import get_notification_service
from src.models import Notification
from src.schemas import NotificationCreateRequest, NotificationCreateResponse
from src.services import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=NotificationCreateResponse,
)
async def create_notification(
    payload: NotificationCreateRequest,
    notification_service: Annotated[
        NotificationService, Depends(get_notification_service)
    ],
) -> Notification:
    return await notification_service.create_notification(
        payload=payload,
    )
