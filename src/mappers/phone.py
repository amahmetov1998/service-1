from typing import Any
from uuid import UUID

from src.models import Phone, User
from src.schemas import PhoneDetailAPIRequest, PhoneNumbers, UserCreateRequest


def orm_to_schema(phones: list[Phone]) -> list[PhoneDetailAPIRequest]:
    return [PhoneDetailAPIRequest.model_validate(phone) for phone in phones]


def orm_to_dict(user: User) -> dict[str, str]:
    phone_numbers = [phone.phone_number for phone in user.phone_numbers]
    return PhoneNumbers(phone_numbers=phone_numbers).model_dump()


def schema_to_dict(payload: UserCreateRequest, user_uuid: UUID) -> list[dict[str, Any]]:
    return [
        {
            **phone.model_dump(),
            "user_uuid": user_uuid,
        }
        for phone in payload.phone_numbers
    ]
