from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from src.enums import UserStatus, PhoneSyncStatus
from .base import Base

if TYPE_CHECKING:
    from .phone import Phone


class User(Base):
    """Модель пользователя"""

    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    status: Mapped[UserStatus] = mapped_column(default=UserStatus.ACTIVE)
    phone_numbers: Mapped[list["Phone"]] = relationship(
        "Phone",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    phone_sync_status: Mapped[PhoneSyncStatus]
    is_deleted: Mapped[bool] = mapped_column(default=False, server_default=sa.false())
