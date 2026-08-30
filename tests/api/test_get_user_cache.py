import pytest


@pytest.mark.asyncio
async def test_get_user_uses_cache(test_client, override_get_redis, cached_user):
    response = await test_client.post(
        "/users",
        json=cached_user,
    )

    user_uuid = response.json()["uuid"]

    key = f"user:{user_uuid}"

    cached = await override_get_redis.get(key)

    assert cached is None
    await test_client.get(f"/users/{user_uuid}")
    cached = await override_get_redis.get(key)
    assert cached is not None

    assert cached["uuid"] == user_uuid
    assert cached["email"] == "cache@example.com"
