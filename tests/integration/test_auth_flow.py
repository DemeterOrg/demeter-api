import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.integration
@pytest.mark.asyncio
async def test_register_user_success(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test User",
            "email": "testuser@example.com",
            "phone": "11999999999",
            "password": "Test123!@#",
            "password_confirm": "Test123!@#",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert data["name"] == "Test User"
    assert "id" in data


@pytest.mark.integration
@pytest.mark.asyncio
async def test_register_duplicate_email_fails(client: AsyncClient):
    user_data = {
        "name": "First User",
        "email": "duplicate@example.com",
        "phone": "11888888888",
        "password": "Test123!@#",
        "password_confirm": "Test123!@#",
    }

    response1 = await client.post("/api/v1/auth/register", json=user_data)
    assert response1.status_code == 201

    response2 = await client.post("/api/v1/auth/register", json=user_data)
    assert response2.status_code == 409


@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_valid_credentials_success(client: AsyncClient):
    register_data = {
        "name": "Login User",
        "email": "loginuser@example.com",
        "phone": "11777777777",
        "password": "Login123!@#",
        "password_confirm": "Login123!@#",
    }
    await client.post("/api/v1/auth/register", json=register_data)

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "loginuser@example.com", "password": "Login123!@#"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "tokens" in data
    assert "access_token" in data["tokens"]
    assert "refresh_token" in data["tokens"]
    assert data["tokens"]["token_type"] == "bearer"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_invalid_credentials_fails(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@example.com", "password": "WrongPass123!"},
    )

    assert response.status_code == 401


@pytest.mark.integration
@pytest.mark.asyncio
async def test_refresh_token_success(client: AsyncClient):
    register_data = {
        "name": "Refresh User",
        "email": "refreshuser@example.com",
        "phone": "11666666666",
        "password": "Refresh123!@#",
        "password_confirm": "Refresh123!@#",
    }
    await client.post("/api/v1/auth/register", json=register_data)

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "refreshuser@example.com", "password": "Refresh123!@#"},
    )
    refresh_token = login_response.json()["tokens"]["refresh_token"]

    response = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_logout_revokes_token(client: AsyncClient):
    register_data = {
        "name": "Logout User",
        "email": "logoutuser@example.com",
        "phone": "11555555555",
        "password": "Logout123!@#",
        "password_confirm": "Logout123!@#",
    }
    await client.post("/api/v1/auth/register", json=register_data)

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "logoutuser@example.com", "password": "Logout123!@#"},
    )
    refresh_token = login_response.json()["tokens"]["refresh_token"]

    response = await client.post(
        "/api/v1/auth/logout", json={"refresh_token": refresh_token}
    )

    assert response.status_code == 200

    refresh_response = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert refresh_response.status_code == 401
