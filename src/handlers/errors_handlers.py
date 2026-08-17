import logging

from fastapi import Request, status
from starlette.responses import JSONResponse

from src.exceptions import (
    NotFoundError,
    AlreadyExistsError,
)

log = logging.getLogger(__name__)


def register_errors_handlers(app):
    @app.exception_handler(NotFoundError)
    def not_found_handler(request: Request, exc: NotFoundError):

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": str(exc),
            },
        )

    @app.exception_handler(AlreadyExistsError)
    def already_exists_handler(request: Request, exc: AlreadyExistsError):

        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"message": str(exc), "detail": exc.details},
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
                "message": "Internal server error",
            },
        )
