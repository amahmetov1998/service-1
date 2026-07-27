from src.models import User
from src.schemas import PhoneDetailAPIResponse, PhoneResponse, UserPhonesResponse


def enrich_phone_numbers(
    phone_details_json: list[dict], user: User
) -> UserPhonesResponse:
    phone_details = [
        PhoneDetailAPIResponse.model_validate(item) for item in phone_details_json
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
    )
