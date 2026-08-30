from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Phone


class PhoneRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def create_phones(self, phones_payload: list[dict]) -> list[Phone]:
        result = await self.session.execute(
            insert(Phone)
            .on_conflict_do_nothing(index_elements=[Phone.phone_number])
            .returning(Phone),
            phones_payload,
        )
        return list(result.scalars().all())
