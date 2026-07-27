from pydantic import BaseModel, EmailStr
from .phone import PhoneCreateRequest, PhoneResponse
from uuid import UUID
from src.core.enums import UserStatus
from .base import BaseResponse
from datetime import datetime


class UserCreateRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_numbers: list[PhoneCreateRequest]


class UserCreateResponse(UserCreateRequest, BaseResponse):
    uuid: UUID


class UserUpdateRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None


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
