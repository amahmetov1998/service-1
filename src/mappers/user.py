from src.models import User, Phone, PhoneSyncStatus
from src.schemas import (
    PhoneDetailAPIResponse,
    PhoneResponse,
    UserPhonesResponse,
    UserSyncResult,
    UserCreateRequest,
)


def response_to_schema(
    phone_details: list[PhoneDetailAPIResponse], user: User
) -> UserPhonesResponse:
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


def orm_to_schema(user: User, phones: list[Phone]) -> UserPhonesResponse:
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
        phone_sync_status=user.phone_sync_status,
    )


def schema_to_orm(results: list[UserSyncResult]) -> list[User]:
    return [
        User(
            uuid=result.uuid,
            attempt_id=result.attempt_id,
            next_retry_at=result.next_retry_at,
            phone_sync_status=result.phone_sync_status,
            retry_count=result.retry_count,
        )
        for result in results
    ]


def request_to_orm(payload: UserCreateRequest, status: PhoneSyncStatus) -> User:
    return User(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        phone_sync_status=status,
    )
