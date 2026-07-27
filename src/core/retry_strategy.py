class RetryBudgetStrategy:
    def __init__(
        self,
        tokens_for_retry: int,
        retry_budget_ratio: float,
        max_retries: int,
    ) -> None:
        self.tokens_for_retry = tokens_for_retry
        self.tokens_to_add_for_success = int(retry_budget_ratio * self.tokens_for_retry)
        self.max_tokens = self.tokens_for_retry * max_retries
        self.tokens = self.max_tokens

    def add_tokens(self) -> None:
        self.tokens = min(self.max_tokens, self.tokens + self.tokens_to_add_for_success)

    def allow_retry(self) -> bool:
        if self.tokens < self.tokens_for_retry:
            return False
        self.tokens -= self.tokens_for_retry
        return True
