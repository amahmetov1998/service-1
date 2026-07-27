import pytest


@pytest.mark.asyncio
async def test_get_user_uses_cache(client, test_redis):
    response = await client.post(
        "/users",
        json={
            "first_name": "Test",
            "last_name": "Test",
            "email": "cache@example.com",
            "phone_numbers": [
                {
                    "phone_number": "+79991234568",
                    "phone_type": "mobile",
                    "is_verified": False,
                    "operator_type": "mts",
                    "region_type": "moscow_city",
                    "is_spam": False,
                }
            ],
        },
    )

    user_uuid = response.json()["uuid"]

    key = f"user_{user_uuid}"

    cached = await test_redis.get(key)

    assert cached is None

    await client.get(f"/users/{user_uuid}")

    cached = await test_redis.get(key)

    assert cached is not None

    assert cached["uuid"] == user_uuid
    assert cached["email"] == "cache@example.com"
