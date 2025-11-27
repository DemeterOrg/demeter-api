import io
from pathlib import Path

import pytest
from httpx import AsyncClient


async def create_and_login_user(client: AsyncClient, email: str) -> str:
    register_data = {
        "name": "ML Test User",
        "email": email,
        "phone": "11988888888",
        "password": "Test123!@#",
        "password_confirm": "Test123!@#",
    }
    await client.post("/api/v1/auth/register", json=register_data)

    login_response = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": "Test123!@#"}
    )
    return login_response.json()["tokens"]["access_token"]


def create_fake_image():
    return io.BytesIO(b"fake image content for testing ML API integration")


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.skipif(
    not Path(".env").exists() or "USE_REAL_ML_API=true" not in Path(".env").read_text(),
    reason="ML API not enabled in .env"
)
async def test_classification_with_ml_api_enabled(client: AsyncClient):
    token = await create_and_login_user(client, "ml_user_1@example.com")

    files = {"image": ("test_grains.jpg", create_fake_image(), "image/jpeg")}
    response = await client.post(
        "/api/v1/classifications",
        files=files,
        data={"notes": "Test with ML API"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code in [201, 422]

    if response.status_code == 201:
        data = response.json()
        assert "id" in data
        assert data["grain_type"] == "Soja"
        assert "confidence_score" in data
        assert data["extra_data"]["mock"] is False
        assert "job_id" in data["extra_data"]
        assert "total_grains" in data["extra_data"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_classification_with_mock_fallback(client: AsyncClient):
    token = await create_and_login_user(client, "ml_user_2@example.com")

    files = {"image": ("test.jpg", create_fake_image(), "image/jpeg")}
    response = await client.post(
        "/api/v1/classifications",
        files=files,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    data = response.json()

    assert "id" in data
    assert "grain_type" in data
    assert "confidence_score" in data

    if "mock" in data["extra_data"]:
        assert isinstance(data["extra_data"]["mock"], bool)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_classification_response_structure(client: AsyncClient):
    token = await create_and_login_user(client, "ml_user_3@example.com")

    files = {"image": ("structure_test.jpg", create_fake_image(), "image/jpeg")}
    response = await client.post(
        "/api/v1/classifications",
        files=files,
        data={"notes": "Validating response structure"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    data = response.json()

    required_fields = ["id", "user_id", "grain_type", "confidence_score",
                      "image_path", "extra_data", "created_at", "updated_at"]
    for field in required_fields:
        assert field in data, f"Missing field: {field}"

    assert isinstance(data["extra_data"], dict)
    assert "mock" in data["extra_data"]
