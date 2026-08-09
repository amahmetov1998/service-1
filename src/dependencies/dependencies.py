from fastapi import Request

from src.config import AppDependencies


def get_dependencies(
    request: Request,
) -> AppDependencies:
    return request.app.state.deps
