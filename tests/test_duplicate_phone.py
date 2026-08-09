import pytest


@pytest.mark.asyncio
async def test_create_user_with_duplicate_phone(test_client, user_with_duplicate_phone):
    response = await test_client.post("/users", json=user_with_duplicate_phone)

    assert response.status_code == 409

    assert response.json() == {"detail": "Resource already exists"}
