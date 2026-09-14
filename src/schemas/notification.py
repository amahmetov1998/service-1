from uuid import UUID

from pydantic import BaseModel, Field

from models.enums import NotificationType


class NotificationCreateRequest(BaseModel):
    user_uuid: UUID
    type: NotificationType
    title: str = Field(max_length=20)
    message: str = Field(max_length=200)


class NotificationCreateResponse(NotificationCreateRequest):
    pass
