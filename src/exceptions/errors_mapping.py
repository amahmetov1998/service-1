from fastapi import status

from .exceptions import (
    InvalidRequestError,
    ValidationError,
)
from .messages import VALIDATION, INVALID_REQUEST

ERRORS = {
    status.HTTP_400_BAD_REQUEST: (InvalidRequestError, INVALID_REQUEST),
    status.HTTP_422_UNPROCESSABLE_CONTENT: (ValidationError, VALIDATION),
}
