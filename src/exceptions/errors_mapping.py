from http import HTTPStatus

from .invalid_request import INVALID_REQUEST
from .invalid_request import InvalidRequestError
from .validation import VALIDATION
from .validation import ValidationError

ERRORS = {
    HTTPStatus.BAD_REQUEST: (InvalidRequestError, INVALID_REQUEST),
    HTTPStatus.UNPROCESSABLE_ENTITY: (ValidationError, VALIDATION),
}
