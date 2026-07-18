import httpx

from exceptions import InvalidPhoneData, PhoneServiceUnavailable
from schemas import PhoneCreateRequest, PhoneDetailAPIRequest


async def send_phone_detail(
    client: httpx.AsyncClient, phone_list: list[PhoneCreateRequest]
) -> list[dict]:
    try:
        response = await client.post(
            "/phones",
            json=[
                PhoneDetailAPIRequest(
                    phone_number=phone.phone_number,
                    operator_type=phone.operator_type,
                    region_type=phone.region_type,
                    is_spam=phone.is_spam,
                ).model_dump()
                for phone in phone_list
            ],
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            raise InvalidPhoneData()
        raise PhoneServiceUnavailable()
    except (httpx.ConnectError, httpx.TimeoutException):
        raise PhoneServiceUnavailable()


async def get_phone_detail(
    client: httpx.AsyncClient, phone_numbers: list[str]
) -> list[dict]:
    try:
        response = await client.get(
            "/phones",
            params={"phone_numbers": phone_numbers},
        )
        response.raise_for_status()
        return response.json()

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            raise InvalidPhoneData()
        raise PhoneServiceUnavailable()
    except (httpx.ConnectError, httpx.TimeoutException):
        raise PhoneServiceUnavailable()
