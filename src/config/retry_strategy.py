class RetryBudgetStrategy:
    def __init__(
        self,
        retry_cost: int,
        retry_budget_ratio: float,
        max_retry_budget: int,
    ) -> None:
        self.retry_cost = retry_cost
        self.success_tokens = int(retry_budget_ratio * self.retry_cost)
        self.max_budget_tokens = self.retry_cost * max_retry_budget
        self.current_tokens = self.max_budget_tokens

    def add_tokens_on_success(self) -> None:
        self.current_tokens = min(
            self.max_budget_tokens, self.current_tokens + self.success_tokens
        )

    def check_retry_attempt(self) -> bool:
        if self.current_tokens < self.retry_cost:
            return False
        self.current_tokens -= self.retry_cost
        return True
