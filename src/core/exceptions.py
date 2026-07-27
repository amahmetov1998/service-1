class UserNotFoundError(Exception):
    pass


class UserAlreadyExistsError(Exception):
    pass


class InvalidPhoneDataError(Exception):
    pass


class PhoneServiceUnavailableError(Exception):
    pass
