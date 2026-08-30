from datetime import timedelta


class RetryBackoffStrategy:
    def __init__(self, max_retry_count_per_user: int, max_backoff: int):
        self.max_retry_count_per_user = max_retry_count_per_user
        self.max_backoff = timedelta(minutes=max_backoff)

    def can_retry(self, retry_count: int) -> bool:
        return retry_count < self.max_retry_count_per_user

    def get_backoff(self, retry_count: int) -> timedelta:
        next_backoff = self._calc_next_backoff(retry_count)
        return self.max_backoff if next_backoff > self.max_backoff else next_backoff

    @staticmethod
    def _calc_next_backoff(retry_count: int) -> timedelta:
        return timedelta(minutes=2**retry_count)
