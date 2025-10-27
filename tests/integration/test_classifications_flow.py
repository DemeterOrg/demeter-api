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


def create_fake_image():
    return io.BytesIO(b"fake image content for testing purposes")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_classification_success(client: AsyncClient):
    token = await create_and_login_user(client, "classifier1@example.com")

    files = {"image": ("test.jpg", create_fake_image(), "image/jpeg")}
    response = await client.post(
        "/api/v1/classifications",
        files=files,
        data={"notes": "Test classification"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert "grain_type" in data
    assert "confidence_score" in data


@pytest.mark.integration
@pytest.mark.asyncio
async def test_list_user_classifications(client: AsyncClient):
    token = await create_and_login_user(client, "classifier2@example.com")

    files = {"image": ("test.jpg", create_fake_image(), "image/jpeg")}
    await client.post(
        "/api/v1/classifications",
        files=files,
        headers={"Authorization": f"Bearer {token}"},
    )

    response = await client.get(
        "/api/v1/classifications", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_classification_success(client: AsyncClient):
    token = await create_and_login_user(client, "classifier3@example.com")

    files = {"image": ("test.jpg", create_fake_image(), "image/jpeg")}
    create_response = await client.post(
        "/api/v1/classifications",
        files=files,
        headers={"Authorization": f"Bearer {token}"},
    )
    classification_id = create_response.json()["id"]

    response = await client.get(
        f"/api/v1/classifications/{classification_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == classification_id


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_other_user_classification_fails(client: AsyncClient):
    token1 = await create_and_login_user(client, "user1@example.com")
    token2 = await create_and_login_user(client, "user2@example.com")

    files = {"image": ("test.jpg", create_fake_image(), "image/jpeg")}
    create_response = await client.post(
        "/api/v1/classifications",
        files=files,
        headers={"Authorization": f"Bearer {token1}"},
    )
    classification_id = create_response.json()["id"]

    response = await client.get(
        f"/api/v1/classifications/{classification_id}",
        headers={"Authorization": f"Bearer {token2}"},
    )

    assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.asyncio
async def test_delete_classification_soft_delete(client: AsyncClient):
    token = await create_and_login_user(client, "deleter@example.com")

    files = {"image": ("test.jpg", create_fake_image(), "image/jpeg")}
    create_response = await client.post(
        "/api/v1/classifications",
        files=files,
        headers={"Authorization": f"Bearer {token}"},
    )
    classification_id = create_response.json()["id"]

    delete_response = await client.delete(
        f"/api/v1/classifications/{classification_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert delete_response.status_code == 200


@pytest.mark.integration
@pytest.mark.asyncio
async def test_deleted_not_in_list(client: AsyncClient):
    token = await create_and_login_user(client, "deleter2@example.com")

    files = {"image": ("test.jpg", create_fake_image(), "image/jpeg")}
    create_response = await client.post(
        "/api/v1/classifications",
        files=files,
        headers={"Authorization": f"Bearer {token}"},
    )
    classification_id = create_response.json()["id"]

    await client.delete(
        f"/api/v1/classifications/{classification_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    list_response = await client.get(
        "/api/v1/classifications", headers={"Authorization": f"Bearer {token}"}
    )

    data = list_response.json()
    assert all(item["id"] != classification_id for item in data["items"])
