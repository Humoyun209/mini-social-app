import uuid

from httpx import AsyncClient

from app.core.security import create_verification_token


async def test_register_user(client: AsyncClient):
    unique = uuid.uuid4().hex[:8]
    user_data = {
        "email": f"new_{unique}@example.com",
        "username": f"newuser_{unique}",
        "full_name": "New User",
        "password": "password123",
    }

    response = await client.post("/api/v1/auth/register", json=user_data)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["is_verified"] is False


async def test_register_duplicate_email(client: AsyncClient, registered_user: dict):
    user_data = {
        "email": registered_user["email"],
        "username": "anotheruser",
        "full_name": "Another User",
        "password": "password123",
    }

    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


async def test_login_user(client: AsyncClient, registered_user: dict):
    login_data = {
        "email": registered_user["email"],
        "password": registered_user["password"],
    }

    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200, f"Login failed: {response.text}"


async def test_login_wrong_password(client: AsyncClient, registered_user: dict):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": registered_user["email"], "password": "wrongpassword"},
    )
    assert response.status_code == 401


async def test_get_current_user(client: AsyncClient, authenticated_user: dict):
    response = await client.get(
        "/api/v1/auth/me",
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 200
    assert response.json()["email"] == authenticated_user["email"]


async def test_get_current_user_without_token(client: AsyncClient):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


async def test_verify_email(client: AsyncClient, registered_user: dict):
    token = create_verification_token(uuid.UUID(registered_user["id"]))

    response = await client.get(f"/api/v1/auth/verify?token={token}")
    assert response.status_code == 200, f"Verify failed: {response.text}"
    assert response.json()["is_verified"] is True


async def test_verify_email_invalid_token(client: AsyncClient):
    response = await client.get("/api/v1/auth/verify?token=invalid_token")
    assert response.status_code == 400


async def test_resend_verification_email(client: AsyncClient, registered_user: dict):
    response = await client.post(
        "/api/v1/auth/resend-verification-email",
        json={"email": registered_user["email"]},
    )
    assert response.status_code == 200


async def test_resend_verification_nonexistent_email(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/resend-verification-email",
        json={"email": "nonexistent@example.com"},
    )
    assert response.status_code == 404
