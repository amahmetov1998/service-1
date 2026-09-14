from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base
from .enums import NotificationType


class Notification(Base):
    """Модель уведомления"""

    user_uuid: Mapped[UUID] = mapped_column(
        ForeignKey("users.uuid", ondelete="CASCADE")
    )
    type: Mapped[NotificationType]
    title: Mapped[str] = mapped_column(String(20))
    message: Mapped[str] = mapped_column(String(200))
