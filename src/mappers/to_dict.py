from uuid import UUID

from src.models import User, Phone
from src.schemas import PhoneDetailAPIRequest, PhoneNumbers, UserCreateRequest


def phones_orm_to_dict(phones: list[Phone]) -> list[dict]:
    return [
        PhoneDetailAPIRequest.model_validate(phone).model_dump() for phone in phones
    ]


def phones_orm_to_list(user: User) -> list[str]:
    phone_numbers = [phone.phone_number for phone in user.phone_numbers]
    return PhoneNumbers(phone_numbers=phone_numbers).model_dump()


def phones_schema_to_dict(payload: UserCreateRequest, user_uuid: UUID) -> list[dict]:
    return [
        {
            **phone.model_dump(),
            "user_uuid": user_uuid,
        }
        for phone in payload.phone_numbers
    ]
