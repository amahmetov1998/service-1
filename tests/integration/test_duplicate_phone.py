import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_create_user_with_duplicate_phone(
    app,
):
    async with app.router.lifespan_context(app):

        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:

            response = await client.post(
                "/users",
                json={
                    "first_name": "Test",
                    "last_name": "Test",
                    "email": "test2@example.com",
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

    assert response.status_code == 400

    assert response.json() == {"detail": "Invalid phone data"}
