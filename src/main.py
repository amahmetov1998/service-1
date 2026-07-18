import uvicorn
import asyncio

from config import settings


async def main() -> None:
    uvicorn.run(
        "application:get_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
        factory=True,
    )


if __name__ == "__main__":
    asyncio.run(main())
