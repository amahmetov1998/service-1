import pytest


@pytest.mark.asyncio
async def test_create_user_with_duplicate_email(test_client, user_with_duplicate_email):
    await test_client.post("/users", json=user_with_duplicate_email)
    response = await test_client.post("/users", json=user_with_duplicate_email)

    assert response.status_code == 409
