import httpx
from tenacity import (
    retry,
    wait_random_exponential,
    RetryCallState,
    retry_if_exception_type,
)
from src.core.exceptions import InvalidPhoneDataError, PhoneServiceUnavailableError
from src.core.retry_strategy import RetryBudgetStrategy
from src.schemas import PhoneCreateRequest, PhoneDetailAPIRequest


class PhoneClient:
    def __init__(
        self,
        client: httpx.AsyncClient,
        retry_strategy: RetryBudgetStrategy,
    ) -> None:
        self.client = client
        self.retry_strategy = retry_strategy

    @staticmethod
    def check_retry_permission(retry_state: RetryCallState):
        strategy = retry_state.args[0].retry_strategy

        if not strategy.allow_retry():
            raise PhoneServiceUnavailableError()

    @retry(
        retry=retry_if_exception_type(PhoneServiceUnavailableError),
        wait=wait_random_exponential(max=60),
        before_sleep=check_retry_permission,
        reraise=True,
    )
    async def send_phone_detail(
        self,
        phone_list: list[PhoneCreateRequest],
    ) -> list[dict]:
        try:
            response = await self.client.post(
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

            self.retry_strategy.add_tokens()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                raise InvalidPhoneDataError()

            raise PhoneServiceUnavailableError()

        except (httpx.ConnectError, httpx.TimeoutException):
            raise PhoneServiceUnavailableError()

    @retry(
        retry=retry_if_exception_type(PhoneServiceUnavailableError),
        wait=wait_random_exponential(max=60),
        before_sleep=check_retry_permission,
        reraise=True,
    )
    async def get_phone_detail(
        self,
        phone_numbers: list[str],
    ) -> list[dict]:
        try:
            response = await self.client.get(
                "/phones",
                params={"phone_numbers": phone_numbers},
            )
            response.raise_for_status()

            self.retry_strategy.add_tokens()
            return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                raise InvalidPhoneDataError()

            raise PhoneServiceUnavailableError()

        except (httpx.ConnectError, httpx.TimeoutException):
            raise PhoneServiceUnavailableError()
