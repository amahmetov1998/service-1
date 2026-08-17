from fastapi import Request
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession


def get_session_factory(
    request: Request,
) -> async_sessionmaker[AsyncSession]:
    return request.app.state.session_factory
