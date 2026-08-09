import httpx

from src.config import settings


def create_http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        base_url=settings.client.base_url,
        timeout=settings.client.timeout,
    )
