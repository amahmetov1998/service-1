import pytest


@pytest.mark.asyncio
async def test_user_lifecycle(client):
    response = await client.post(
        "/users",
        json={
            "first_name": "Test",
            "last_name": "Test",
            "email": "test@example.com",
            "phone_numbers": [
                {
                    "phone_number": "+79991234567",
                    "phone_type": "mobile",
                    "is_verified": "false",
                    "operator_type": "mts",
                    "region_type": "moscow_city",
                    "is_spam": False,
                }
            ],
        },
    )

    assert response.status_code == 201

    user = response.json()
    user_uuid = user["uuid"]

    response = await client.get(f"/users/{user_uuid}")

    assert response.status_code == 200

    response = await client.patch(
        f"/users/{user_uuid}",
        json={
            "first_name": "New name",
        },
    )
    updated_user = response.json()

    assert updated_user["first_name"] == "New name"
    assert updated_user["uuid"] == user_uuid

    response = await client.delete(f"/users/{user_uuid}")

    assert response.status_code == 204
