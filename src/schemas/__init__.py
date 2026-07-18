__all__ = [
    "UserCreateRequest",
    "PhoneCreateRequest",
    "UserCreateResponse",
    "UserPhonesResponse",
    "UserDeleteResponse",
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
    UserDeleteResponse,
)

from .phone import PhoneResponse, PhoneCreateRequest
