__all__ = [
    "UserCreateRequest",
    "PhoneCreateRequest",
    "UserCreateResponse",
    "UserPhonesResponse",
    "UserUpdateResponse",
    "UserUpdateRequest",
    "PhoneDetailAPIRequest",
    "PhoneDetailAPIResponse",
    "PhoneResponse",
]

from .external import PhoneDetailAPIRequest, PhoneDetailAPIResponse

from .user import (
    UserCreateRequest,
    UserCreateResponse,
    UserPhonesResponse,
    UserUpdateResponse,
    UserUpdateRequest,
)

from .phone import PhoneResponse, PhoneCreateRequest
