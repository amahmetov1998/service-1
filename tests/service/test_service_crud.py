import pytest

from src.dependencies import get_uow
from src.exceptions import NotFoundError
from src.models import PhoneSyncStatus
from src.schemas import UserCreateRequest, UserUpdateRequest
from src.services.user import UserService


@pytest.mark.asyncio
async def test_user_service_crud(
    override_get_session_factory,
    override_get_redis,
    override_get_service_phone_client,
    user_service_payload,
):
    uow_factory = get_uow(
        session_factory=override_get_session_factory,
    )

    service = UserService(
        phone_client=override_get_service_phone_client,
        uow_factory=uow_factory,
        redis=override_get_redis,
    )

    payload = UserCreateRequest.model_validate(user_service_payload)

    user = await service.create_user(payload)

    assert user.email == user_service_payload["email"]
    assert user.first_name == user_service_payload["first_name"]
    assert user.phone_sync_status == PhoneSyncStatus.DONE

    user_uuid = user.uuid

    user = await service.get_user(user_uuid)

    assert user.uuid == user_uuid
    assert user.email == user_service_payload["email"]

    user = await service.update_user(
        user_uuid=user_uuid,
        payload=UserUpdateRequest(first_name="New name"),
    )

    assert user.first_name == "New name"
    assert user.uuid == user_uuid

    await service.delete_user(user_uuid)

    with pytest.raises(NotFoundError):
        await service.get_user(user_uuid)
