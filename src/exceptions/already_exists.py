from src.schemas import AlreadyExistsDetails


class AlreadyExistsError(Exception):
    def __init__(self, message: str, details: AlreadyExistsDetails | None = None):
        super().__init__(message)
        self.details = details
