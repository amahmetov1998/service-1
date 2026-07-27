from starlette.responses import JSONResponse

from src.core.exceptions import (
    UserNotFoundError,
    InvalidPhoneDataError,
    PhoneServiceUnavailableError,
    UserAlreadyExistsError,
)

from sqlalchemy.exc import IntegrityError
from fastapi import Request, status


def register_errors_handlers(app):
    @app.exception_handler(UserNotFoundError)
    def user_not_found_handler(request: Request, exc: UserNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "detail": "User not found",
            },
        )

    @app.exception_handler(InvalidPhoneDataError)
    def invalid_phone_data_handler(request: Request, exc: InvalidPhoneDataError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Invalid phone data"},
        )

    @app.exception_handler(PhoneServiceUnavailableError)
    def phone_service_unavailable_handler(
        request: Request, exc: PhoneServiceUnavailableError
    ):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Phone services unavailable"},
        )

    @app.exception_handler(UserAlreadyExistsError)
    def user_already_exists_handler(request: Request, exc: UserAlreadyExistsError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "User already exists"},
        )

    @app.exception_handler(IntegrityError)
    def integrity_error_handler(request: Request, exc: IntegrityError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Invalid data"},
        )
