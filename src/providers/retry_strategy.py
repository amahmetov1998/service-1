from src.config import RetryBudgetStrategy, settings


def create_retry_strategy() -> RetryBudgetStrategy:
    return RetryBudgetStrategy(
        tokens_for_retry=settings.retry.tokens_for_retry,
        retry_budget_ratio=settings.retry.retry_budget_ratio,
        max_retries=settings.retry.max_retries_global,
    )
