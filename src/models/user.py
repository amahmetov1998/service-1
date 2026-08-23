from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from src.models import PhoneSyncStatus
from .base import Base

if TYPE_CHECKING:
    from .phone import Phone


class User(Base):
    """Модель пользователя"""

    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    phone_numbers: Mapped[list["Phone"]] = relationship(
        "Phone",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    phone_sync_status: Mapped[PhoneSyncStatus | None]
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    next_retry_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
