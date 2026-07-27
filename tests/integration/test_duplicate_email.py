import pytest


@pytest.mark.asyncio
async def test_create_user_with_duplicate_email(client):
    await client.post(
        "/users",
        json={
            "first_name": "Test",
            "last_name": "Test",
            "email": "test@example.com",
            "phone_numbers": [
                {
                    "phone_number": "+79991534567",
                    "phone_type": "mobile",
                    "is_verified": "false",
                    "operator_type": "mts",
                    "region_type": "moscow_city",
                    "is_spam": False,
                }
            ],
        },
    )
    response = await client.post(
        "/users",
        json={
            "first_name": "Ivan",
            "last_name": "Ivanov",
            "email": "test@example.com",
            "phone_numbers": [
                {
                    "phone_number": "+9289487291",
                    "phone_type": "mobile",
                    "is_verified": "false",
                    "operator_type": "mts",
                    "region_type": "moscow_city",
                    "is_spam": False,
                }
            ],
        },
    )

    assert response.status_code == 409
