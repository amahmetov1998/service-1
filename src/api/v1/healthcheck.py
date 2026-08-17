from fastapi import APIRouter

from src.schemas import HealthCheck

router = APIRouter()


@router.get("/healthcheck")
async def healthcheck() -> HealthCheck:
    return HealthCheck(status="ok")
