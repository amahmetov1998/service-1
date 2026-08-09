import logging
from typing import Callable, Awaitable, Any

import httpx
from tenacity import (
    retry,
    wait_random_exponential,
    RetryCallState,
    retry_if_exception_type,
    retry_if_result,
    retry_any,
)

from src.config import RetryBudgetStrategy, settings
from src.exceptions import (
    ERRORS,
    PHONE_DATA_ALREADY_EXISTS,
    RETRIES_EXCEEDED,
    PHONE_DATA_NOT_FOUND,
    RetriesLimitError,
    NotFoundError,
    AlreadyExistsError,
)

log = logging.getLogger(__name__)


class PhoneClient:
    def __init__(
        self,
        client: httpx.AsyncClient,
        retry_strategy: RetryBudgetStrategy,
        url: str = "/phones",
    ) -> None:
        self.url = url
        self.client = client
        self.retry_strategy = retry_strategy

    @staticmethod
    def check_retry_permission(retry_state: RetryCallState):
        log.debug(
            "Retrying request: attempt=%s",
            retry_state.attempt_number,
        )
        strategy = retry_state.args[0].retry_strategy
        if not strategy.allow_retry():
            log.warning("Retry limit exceeded: retries are no longer allowed")
            raise RetriesLimitError(RETRIES_EXCEEDED)

    async def post(
        self,
        payload: list[dict],
    ):
        response = await self._make_request(self.client.post, json=payload)
        if response.status_code == 409:
            log.warning(
                "Service rejected the request with status code: %s, reason: %s",
                response.status_code,
                PHONE_DATA_ALREADY_EXISTS,
            )
            raise AlreadyExistsError(PHONE_DATA_ALREADY_EXISTS)

        self.retry_strategy.add_tokens()

        return response

    async def get(
        self,
        params: list[str],
    ) -> httpx.Response:

        response = await self._make_request(self.client.get, params=params)

        if response.status_code == 404:
            log.warning(
                "Service rejected the request with status code: %s, reason: %s",
                response.status_code,
                PHONE_DATA_NOT_FOUND,
            )
            raise NotFoundError(PHONE_DATA_NOT_FOUND)

        self.retry_strategy.add_tokens()

        return response

    @retry(
        retry=retry_any(
            retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError))
            | retry_if_result(lambda r: r.status_code >= 500)
        ),
        wait=wait_random_exponential(max=settings.retry.max_retry_delay_seconds),
        before_sleep=check_retry_permission,
        reraise=True,
    )
    async def _make_request(
        self,
        request_method: Callable[..., Awaitable[httpx.Response]],
        **kwargs: Any,
    ) -> httpx.Response:
        response = await request_method(self.url, **kwargs)
        error = ERRORS.get(response.status_code)
        if error:
            exc, msg = error
            log.warning(
                "Service rejected the request with status code: %s, reason: %s",
                response.status_code,
                msg,
            )
            raise exc(msg)
        return response
