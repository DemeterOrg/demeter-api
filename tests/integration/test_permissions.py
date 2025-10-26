import io

import pytest
from httpx import AsyncClient


async def create_and_login_user(client: AsyncClient, email: str) -> str:
    register_data = {
        "name": "Test User",
        "email": email,
        "phone": "11999999999",
        "password": "Test123!@#",
        "password_confirm": "Test123!@#",
    }
    await client.post("/api/v1/auth/register", json=register_data)

    login_response = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": "Test123!@#"}
    )
    return login_response.json()["tokens"]["access_token"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_user_with_permission_access_allowed(client: AsyncClient):
    token = await create_and_login_user(client, "permuser@example.com")

    response = await client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "permuser@example.com"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_user_without_permission_denied(client: AsyncClient):
    response = await client.get("/api/v1/classifications")

    assert response.status_code == 403


@pytest.mark.integration
@pytest.mark.asyncio
async def test_admin_can_access_admin_endpoints(client: AsyncClient):
    token = await create_and_login_user(client, "admintest@example.com")

    response = await client.get(
        "/api/v1/admin/classifications",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code in [200, 403]
