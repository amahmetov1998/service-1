from src.schemas import NotFoundDetails


class NotFoundError(Exception):
    def __init__(self, message: str, details: NotFoundDetails | None = None):
        super().__init__(message)
        self.details = details
