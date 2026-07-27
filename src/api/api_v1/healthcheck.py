from fastapi import APIRouter, Depends

from src.clients import PhoneClient
from src.core.dependencies import get_phone_client

router = APIRouter()


@router.get("/healthcheck")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/test-external")
async def external(
    client: PhoneClient = Depends(get_phone_client),
):
    response = await client.client.get("/healthcheck")

    return response.json()
