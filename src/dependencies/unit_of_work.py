from typing import Annotated, Callable

from fastapi import Depends

from src.config import AppDependencies, UnitOfWork
from src.providers import create_uow_factory
from .dependencies import get_dependencies


def get_uow(
    deps: Annotated[AppDependencies, Depends(get_dependencies)],
) -> Callable[[], UnitOfWork]:
    return create_uow_factory(deps)
