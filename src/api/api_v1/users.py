from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.core.dependencies import get_user_service
from src.models import User
from src.schemas import (
    UserCreateRequest,
    UserCreateResponse,
    UserPhonesResponse,
    UserUpdateResponse,
    UserUpdateRequest,
)

from src.services import UserService

router = APIRouter()


@router.get("/users/{user_uuid}")
async def get_user_phones(
    user_uuid: UUID,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserPhonesResponse:
    return await user_service.get_user_with_phones(
        user_uuid=user_uuid,
    )


@router.post(
    "/users",
    response_model=UserCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user_with_phones(
    payload: UserCreateRequest,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> User:
    return await user_service.create_user_with_phones(
        payload=payload,
    )


@router.delete(
    "/users/{user_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_uuid: UUID,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> None:
    return await user_service.delete_user(
        user_uuid=user_uuid,
    )


@router.patch(
    "/users/{user_uuid}",
    response_model=UserUpdateResponse,
    status_code=status.HTTP_200_OK,
)
async def update_user(
    user_uuid: UUID,
    payload: UserUpdateRequest,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> User:
    return await user_service.update_user(
        user_uuid,
        payload=payload,
    )
