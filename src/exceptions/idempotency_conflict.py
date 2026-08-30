from src.schemas import IdempotencyConflictDetails


class IdempotencyConflictError(Exception):
    def __init__(self, message: str, details: IdempotencyConflictDetails):
        super().__init__(message)
        self.details = details
