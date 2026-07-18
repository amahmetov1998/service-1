from sqlalchemy.orm import DeclarativeBase, declared_attr
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import func
from sqlalchemy.orm import mapped_column, Mapped


class Base(DeclarativeBase):
    """Базовый класс для таблиц сервиса."""

    __abstract__ = True

    uuid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"
