from .notification_service import get_notification_service
from .redis import get_redis
from .retry_strategy import get_retry_strategy
from .service_phone_client import get_service_phone_client
from .session_factory import get_session_factory
from .uow import get_uow
from .user_service import get_user_service

__all__ = (
    "get_user_service",
    "get_uow",
    "get_redis",
    "get_service_phone_client",
    "get_retry_strategy",
    "get_session_factory",
    "get_notification_service",
)
