from starlette.responses import JSONResponse

from exceptions import (
    UserNotFound,
    InvalidPhoneData,
    PhoneServiceUnavailable,
    UserAlreadyExists,
)

from sqlalchemy.exc import IntegrityError
from fastapi import Request, status


def register_errors_handlers(app):
    @app.exception_handler(UserNotFound)
    def user_not_found_handler(request: Request, exc: UserNotFound):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "detail": "User not found",
            },
        )

    @app.exception_handler(InvalidPhoneData)
    def invalid_phone_data_handler(request: Request, exc: InvalidPhoneData):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Invalid phone data"},
        )

    @app.exception_handler(PhoneServiceUnavailable)
    def phone_service_unavailable_handler(
        request: Request, exc: PhoneServiceUnavailable
    ):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Phone service unavailable"},
        )

    @app.exception_handler(UserAlreadyExists)
    def user_already_exists_handler(request: Request, exc: UserAlreadyExists):
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
