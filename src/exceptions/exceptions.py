class NotFoundError(Exception):
    pass


class AlreadyExistsError(Exception):
    pass


class ValidationError(Exception):
    pass


class InvalidRequestError(Exception):
    pass


class RetriesLimitError(Exception):
    pass
