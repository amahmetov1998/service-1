from src.clients import PhoneClient
from src.config import AppDependencies, WorkDependencies


def create_phone_client(deps: AppDependencies | WorkDependencies) -> PhoneClient:
    return PhoneClient(
        client=deps.http_client,
        retry_strategy=deps.retry_strategy,
    )
