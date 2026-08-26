from typing import Any

from pydantic import BaseModel


class AlreadyExistsDetails(BaseModel):
    detail: list[str]


class NotFoundDetails(BaseModel):
    detail: list[str]


class InvalidFormatDetails(BaseModel):
    detail: str


class ErrorResponse(BaseModel):
    message: str
    details: Any | None = None
