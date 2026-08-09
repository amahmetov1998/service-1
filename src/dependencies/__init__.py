from .client import get_phone_client
from .dependencies import get_dependencies
from .service import get_user_service

__all__ = [
    "get_dependencies",
    "get_phone_client",
    "get_user_service",
]
