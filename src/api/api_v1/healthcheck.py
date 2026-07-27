from fastapi import APIRouter, Depends

from src.clients import PhoneClient
from src.core.dependencies import get_phone_client

router = APIRouter()


@router.get("/healthcheck")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
