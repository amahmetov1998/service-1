from typing import Annotated

from fastapi import Depends

from src.clients import PhoneClient
from src.config import AppDependencies
from src.providers import create_phone_client
from .dependencies import get_dependencies


def get_phone_client(
    deps: Annotated[AppDependencies, Depends(get_dependencies)],
) -> PhoneClient:
    return create_phone_client(deps)
