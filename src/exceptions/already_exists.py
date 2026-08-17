PHONE_DATA_EXISTS = "Phone data already exists"
USER_EXISTS = "User already exists"


class AlreadyExistsError(Exception):
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.details = details
