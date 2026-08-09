import logging

from fastapi import Request, status
from starlette.responses import JSONResponse

from src.exceptions import (
    NotFoundError,
    ValidationError,
    AlreadyExistsError,
    InvalidRequestError,
)

log = logging.getLogger(__name__)


def register_errors_handlers(app):
    @app.exception_handler(NotFoundError)
    def not_found_handler(request: Request, exc: NotFoundError):

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "detail": "Resource not found",
            },
        )

    @app.exception_handler(ValidationError)
    def validation_handler(request: Request, exc: ValidationError):

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "detail": "Invalid request",
            },
        )

    @app.exception_handler(InvalidRequestError)
    def invalid_request_handler(request: Request, exc: InvalidRequestError):

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": "Invalid request format",
            },
        )

    @app.exception_handler(AlreadyExistsError)
    def already_exists_handler(request: Request, exc: AlreadyExistsError):

        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "detail": "Resource already exists",
            },
        )

    @app.exception_handler(Exception)
    async def unexpected_exception_handler(
        request: Request,
        exc: Exception,
    ):
        log.exception(
            "Unhandled exception: method=%s path=%s",
            request.method,
            request.url.path,
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error",
            },
        )
