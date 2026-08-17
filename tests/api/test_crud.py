import pytest

from src.models import PhoneSyncStatus


@pytest.mark.asyncio
async def test_crud(test_client, user_payload):
    response = await test_client.post("/users", json=user_payload)
    assert response.status_code == 201

    user = response.json()
    assert user["phone_sync_status"] == PhoneSyncStatus.DONE
    user_uuid = user["uuid"]

    response = await test_client.get(f"/users/{user_uuid}")

    assert response.status_code == 200

    response = await test_client.patch(
        f"/users/{user_uuid}",
        json={
            "first_name": "New name",
        },
    )
    updated_user = response.json()

    assert updated_user["first_name"] == "New name"
    assert updated_user["uuid"] == user_uuid

    response = await test_client.delete(f"/users/{user_uuid}")

    assert response.status_code == 204
