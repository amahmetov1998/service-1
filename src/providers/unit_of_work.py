from typing import Callable

from src.config import AppDependencies, WorkDependencies
from src.config.unit_of_work import UnitOfWork


def create_uow_factory(
    deps: AppDependencies | WorkDependencies,
) -> Callable[[], UnitOfWork]:
    return lambda: UnitOfWork(session_factory=deps.session_factory)
