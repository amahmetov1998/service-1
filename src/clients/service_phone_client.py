import functools
import logging
from http import HTTPStatus
from typing import Callable, Awaitable, Any

import httpx
from tenacity import (
    wait_random_exponential,
    RetryCallState,
    retry_if_exception_type,
    retry_if_result,
    AsyncRetrying,
    retry_any,
)

from src.config import RetryBudgetStrategy, settings
from src.exceptions import (
    RetriesLimitError,
    NotFoundError,
    AlreadyExistsError,
    ServiceUnavailableError,
)
from src.schemas import PhoneDetailAPIRequest, PhoneNumbers

log = logging.getLogger(__name__)


def handle_transport_errors(request_func):
    @functools.wraps(request_func)
    async def wrapper(*args, **kwargs):
        try:
            return await request_func(*args, **kwargs)
        except (
            httpx.TimeoutException,
            httpx.NetworkError,
            RetriesLimitError,
        ) as e:
            log.warning(
                "Service not available. Error type=%s, error=%s", type(e).__name__, e
            )
            raise ServiceUnavailableError("Phone service unavailable")

    return wrapper


class ServicePhoneClient:
    def __init__(
        self,
        client: httpx.AsyncClient,
        retry_strategy: RetryBudgetStrategy,
        url: str = "/phones",
    ) -> None:
        self.url = url
        self.client = client
        self.retry_strategy = retry_strategy

    @handle_transport_errors
    async def send_phones(
        self,
        payload: list[PhoneDetailAPIRequest],
    ) -> None:
        service_payload = [phone.model_dump() for phone in payload]
        response = await self._make_request(
            request_method=self.client.post, json=service_payload
        )
        if response.status_code == HTTPStatus.CONFLICT:
            raise AlreadyExistsError("Phone data already exists")

        self.retry_strategy.add_tokens_on_success()

    @handle_transport_errors
    async def get_phones(
        self,
        params: PhoneNumbers,
    ) -> list[dict[str, str]]:
        response = await self._make_request(self.client.get, params=params.model_dump())

        if response.status_code == HTTPStatus.NOT_FOUND:
            log.warning(
                "Service rejected the request with status code: %s. Phone data not found",
                response.status_code,
            )
            raise NotFoundError("Phone data not found")

        self.retry_strategy.add_tokens_on_success()

        return response.json()

    async def _make_request(
        self,
        request_method: Callable[..., Awaitable[httpx.Response]],
        **kwargs: Any,
    ) -> httpx.Response:
        async for attempt in AsyncRetrying(
            retry=retry_any(
                retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
                retry_if_result(lambda response: response.status_code >= 500),
            ),
            wait=wait_random_exponential(max=settings.retry.max_retry_delay_seconds),
            reraise=True,
            before_sleep=self.check_retry_permission,
        ):
            with attempt:
                response = await request_method(self.url, **kwargs)

            if attempt.retry_state.outcome.failed:
                raise attempt.retry_state.outcome.exception()

            attempt.retry_state.set_result(response)

        return response

    def check_retry_permission(self, retry_state: RetryCallState):
        log.debug(
            "Retrying request: attempt=%s",
            retry_state.attempt_number,
        )
        if not self.retry_strategy.check_retry_attempt():
            log.warning("Retry limit exceeded: retries are no longer allowed")
            raise RetriesLimitError("Retry limit exceeded")
