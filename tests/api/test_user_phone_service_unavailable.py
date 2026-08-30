import pytest


@pytest.mark.asyncio
async def test_create_user_phone_service_unavailable(
    client_with_unavailable_service, user_unavailable_service
):
    response = await client_with_unavailable_service.post(
        "/users", json=user_unavailable_service
    )

    assert response.status_code == 201

    user = response.json()

    assert user["phone_sync_status"] == "pending"
