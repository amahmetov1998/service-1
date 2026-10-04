from typing import Any

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Phone


class PhoneRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def create_phones(self, phones: list[dict[str, Any]]) -> list[Phone]:
        result = await self.session.execute(
            insert(Phone)
            .on_conflict_do_nothing(index_elements=[Phone.phone_number])
            .returning(Phone),
            phones,
        )
        return list(result.scalars().all())
