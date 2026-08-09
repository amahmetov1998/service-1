from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.enums import PhoneSyncStatus
from src.enums import UserStatus
from .base import BaseResponse
from .phone import PhoneCreateRequest, PhoneResponse


def check_name(v: str) -> str:
    if not isinstance(v, str):
        raise ValueError("Field must be a string")
    return v


def check_optional_name(v: str | None) -> str | None:
    if v is None:
        return v
    if not isinstance(v, str):
        raise ValueError("Field must be a string")
    return v


class UserCreateRequest(BaseModel):
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    email: EmailStr
    phone_numbers: list[PhoneCreateRequest]

    @field_validator("first_name", "last_name", mode="before")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return check_name(v)


class UserUpdateRequest(BaseModel):
    first_name: str | None = Field(default=None, max_length=50)
    last_name: str | None = Field(default=None, max_length=50)
    email: EmailStr | None = None

    @field_validator("first_name", "last_name", mode="before")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        return check_optional_name(v)


class UserUpdateResponse(BaseResponse):
    uuid: UUID
    first_name: str
    last_name: str
    email: EmailStr
    status: UserStatus
    created_at: datetime


class UserPhonesResponse(BaseResponse):
    uuid: UUID
    first_name: str
    last_name: str
    email: EmailStr
    phone_numbers: list[PhoneResponse]
    phone_sync_status: PhoneSyncStatus
