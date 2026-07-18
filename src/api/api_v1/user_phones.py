from typing import Annotated
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_http_client
from models import User
from schemas import (
    UserCreateRequest,
    UserCreateResponse,
    UserPhonesResponse,
    UserUpdateResponse,
    UserDeleteResponse,
    UserUpdateRequest,
)
from utils.db_helper import db_helper

from src.service import user as user_phones_service

router = APIRouter()


@router.get("/users/{user_uuid}")
async def get_user_phones(
    user_uuid: UUID,
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
    http_client: Annotated[httpx.AsyncClient, Depends(get_http_client)],
) -> UserPhonesResponse:
    return await user_phones_service.get_user_with_phones(
        session, user_uuid, http_client
    )


@router.post("/users", response_model=UserCreateResponse)
async def create_user_with_phones(
    payload: UserCreateRequest,
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
    http_client: Annotated[httpx.AsyncClient, Depends(get_http_client)],
) -> User:
    return await user_phones_service.create_user_with_phones(
        session, payload, http_client
    )


@router.delete("/users/{user_uuid}", response_model=UserDeleteResponse)
async def delete_user(
    user_uuid: UUID,
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
) -> User:
    return await user_phones_service.delete_user(session, user_uuid)


@router.patch("/users/{user_uuid}", response_model=UserUpdateResponse)
async def update_user(
    payload: UserUpdateRequest,
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
) -> User:
    return await user_phones_service.update_user(session, payload)
