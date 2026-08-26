from src.schemas import InvalidFormatDetails


class InvalidFormatError(Exception):
    def __init__(self, message: str, details: InvalidFormatDetails):
        super().__init__(message)
        self.details = details
