from fastapi import APIRouter

from .healthcheck import router as healthcheck_router
from .user_phones import router as user_phones_router

router = APIRouter()
router.include_router(healthcheck_router)
router.include_router(user_phones_router)
