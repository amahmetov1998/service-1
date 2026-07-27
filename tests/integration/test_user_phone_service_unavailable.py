import pytest


@pytest.mark.asyncio
async def test_create_user_phone_service_unavailable(fake_client):
    response = await fake_client.post(
        "/users",
        json={
            "first_name": "Test",
            "last_name": "Test",
            "email": "fail@example.com",
            "phone_numbers": [
                {
                    "phone_number": "+79991234568",
                    "phone_type": "mobile",
                    "is_verified": "false",
                    "operator_type": "mts",
                    "region_type": "moscow_city",
                    "is_spam": False,
                }
            ],
        },
    )

    assert response.status_code == 503
