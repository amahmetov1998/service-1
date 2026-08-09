from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from src.enums import PhoneType, OperatorType, RegionType
from .base import Base

if TYPE_CHECKING:
    from .user import User


class Phone(Base):
    """Модель номера телефона"""

    user_uuid: Mapped[UUID] = mapped_column(
        ForeignKey("users.uuid", ondelete="CASCADE"), nullable=False
    )
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    phone_type: Mapped[PhoneType] = mapped_column(
        default=PhoneType.HOME,
        nullable=False,
    )
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="phone_numbers")

    operator_type: Mapped[OperatorType]
    region_type: Mapped[RegionType]
    is_spam: Mapped[bool]
