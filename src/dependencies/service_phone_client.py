from fastapi import Request

from src.clients import ServicePhoneClient


def get_service_phone_client(
    request: Request,
) -> ServicePhoneClient:
    return request.app.state.service_phone_client
