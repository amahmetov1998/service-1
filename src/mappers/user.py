from typing import Any

from src.models import User, Phone, PhoneSyncStatus
from src.schemas import (
    PhoneDetailAPIResponse,
    PhoneResponse,
    UserPhonesResponse,
    UserSyncResult,
)


def dict_to_schema(
    phone_details: list[dict[str, str]], user: User
) -> UserPhonesResponse:
    phone_details = [
        PhoneDetailAPIResponse.model_validate(item) for item in phone_details
    ]
    phone_details_map = {item.phone_number: item for item in phone_details}
    phones = []
    for phone in user.phone_numbers:
        detail = phone_details_map.get(phone.phone_number)
        if detail:
            phones.append(
                PhoneResponse(
                    phone_number=phone.phone_number,
                    phone_type=phone.phone_type,
                    is_verified=phone.is_verified,
                    operator_type=detail.operator_type,
                    region_type=detail.region_type,
                    is_spam=detail.is_spam,
                )
            )
    return UserPhonesResponse(
        uuid=user.uuid,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        phone_numbers=phones,
        phone_sync_status=user.phone_sync_status,
    )


def orm_to_schema(
    user: User, phones: list[Phone], status: PhoneSyncStatus | None
) -> UserPhonesResponse:
    phones = [
        PhoneResponse(
            phone_number=phone.phone_number,
            phone_type=phone.phone_type,
            is_verified=phone.is_verified,
            operator_type=phone.operator_type,
            region_type=phone.region_type,
            is_spam=phone.is_spam,
        )
        for phone in phones
    ]
    return UserPhonesResponse(
        uuid=user.uuid,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        phone_numbers=phones,
        phone_sync_status=status,
    )


def schema_to_dict(sync_results: list[UserSyncResult]) -> list[dict[str, str]]:
    return [user.model_dump() for user in sync_results]


def orm_to_dict(users: list[User]) -> list[dict[str, Any]]:
    return [
        {
            "uuid": user.uuid,
            "phone_sync_status": PhoneSyncStatus.PROCESSING,
        }
        for user in users
    ]
