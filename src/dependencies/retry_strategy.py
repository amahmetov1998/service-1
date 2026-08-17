from fastapi import Request

from src.config import RetryBudgetStrategy


def get_retry_strategy(
    request: Request,
) -> RetryBudgetStrategy:
    return request.app.state.retry_strategy
