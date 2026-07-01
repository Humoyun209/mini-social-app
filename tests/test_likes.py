import random
import uuid
import pytest
from httpx import AsyncClient


async def test_like_post(client: AsyncClient, authenticated_user: dict):
    """Пользователь может лайкнуть чужой пост"""
    # Регистрируем второго пользователя и создаём пост от него
    unique = uuid.uuid4().hex[:8]
    reg_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": f"author_{unique}@example.com",
            "username": f"author_{unique}",
            "full_name": "Author",
            "password": "password123",
        },
    )
    user_id = reg_response.json()["id"]

    # Верифицируем и логиним автора
    from app.core.security import create_verification_token

    token = create_verification_token(uuid.UUID(user_id))
    await client.get(f"/api/v1/auth/verify?token={token}")

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": f"author_{unique}@example.com", "password": "password123"},
    )
    author_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    # Создаём пост от автора
    post_response = await client.post(
        "/api/v1/posts",
        json={"title": "Author Post", "content": "Content"},
        headers=author_headers,
    )
    post_id = post_response.json()["id"]

    # Лайкаем от имени authenticated_user
    response = await client.post(
        f"/api/v1/posts/{post_id}/like",
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 201

    data = response.json()
    assert data["user_id"] == authenticated_user["id"]
    assert data["post_id"] == post_id


async def test_like_own_post(client: AsyncClient, authenticated_user: dict):
    """Нельзя лайкать свой пост"""
    post_response = await client.post(
        "/api/v1/posts",
        json={"title": "My Post", "content": "Content"},
        headers=authenticated_user["headers"],
    )
    post_id = post_response.json()["id"]

    response = await client.post(
        f"/api/v1/posts/{post_id}/like",
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 400
    assert "cannot like your own post" in response.json()["detail"].lower()


async def test_like_twice(client: AsyncClient, authenticated_user: dict):
    """Нельзя лайкать один пост дважды"""
    # Создаём пост от другого пользователя (используем registered_user pattern)
    unique = uuid.uuid4().hex[:8]
    reg_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": f"author2_{unique}@example.com",
            "username": f"author2_{unique}",
            "full_name": "Author",
            "password": "password123",
        },
    )
    user_id = reg_response.json()["id"]

    from app.core.security import create_verification_token

    token = create_verification_token(uuid.UUID(user_id))
    await client.get(f"/api/v1/auth/verify?token={token}")

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": f"author2_{unique}@example.com", "password": "password123"},
    )
    author_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    post_response = await client.post(
        "/api/v1/posts",
        json={"title": f"Post - {random.random()}", "content": "Content"},
        headers=author_headers,
    )
    post_id = post_response.json()["id"]

    # Первый лайк
    response1 = await client.post(
        f"/api/v1/posts/{post_id}/like",
        headers=authenticated_user["headers"],
    )
    assert response1.status_code == 201

    # Второй лайк — ошибка
    response2 = await client.post(
        f"/api/v1/posts/{post_id}/like",
        headers=authenticated_user["headers"],
    )
    assert response2.status_code == 400
    assert "already liked" in response2.json()["detail"].lower()


async def test_like_nonexistent_post(client: AsyncClient, authenticated_user: dict):
    """Лайк несуществующего поста — 404"""
    fake_id = uuid.uuid4()
    response = await client.post(
        f"/api/v1/posts/{fake_id}/like",
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 404


async def test_unlike_post(client: AsyncClient, authenticated_user: dict):
    """Пользователь может убрать лайк"""
    # Создаём пост от другого пользователя
    unique = uuid.uuid4().hex[:8]
    reg_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": f"author3_{unique}@example.com",
            "username": f"author3_{unique}",
            "full_name": "Author",
            "password": "password123",
        },
    )
    user_id = reg_response.json()["id"]

    from app.core.security import create_verification_token

    token = create_verification_token(uuid.UUID(user_id))
    await client.get(f"/api/v1/auth/verify?token={token}")

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": f"author3_{unique}@example.com", "password": "password123"},
    )
    author_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    post_response = await client.post(
        "/api/v1/posts",
        json={"title": f"Post - {random.random()}", "content": "Content"},
        headers=author_headers,
    )
    post_id = post_response.json()["id"]

    # Лайкаем
    await client.post(
        f"/api/v1/posts/{post_id}/like",
        headers=authenticated_user["headers"],
    )

    # Убираем лайк
    response = await client.delete(
        f"/api/v1/posts/{post_id}/like",
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 204


async def test_unlike_not_liked(client: AsyncClient, authenticated_user: dict):
    """Убрать лайк которого нет — 404"""
    # Создаём пост от другого пользователя
    unique = uuid.uuid4().hex[:8]
    reg_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": f"author4_{unique}@example.com",
            "username": f"author4_{unique}",
            "full_name": "Author",
            "password": "password123",
        },
    )
    user_id = reg_response.json()["id"]

    from app.core.security import create_verification_token

    token = create_verification_token(uuid.UUID(user_id))
    await client.get(f"/api/v1/auth/verify?token={token}")

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": f"author4_{unique}@example.com", "password": "password123"},
    )
    author_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    post_response = await client.post(
        "/api/v1/posts",
        json={"title": f"Post - {random.random()}", "content": "Content"},
        headers=author_headers,
    )
    post_id = post_response.json()["id"]

    # Убираем лайк которого нет
    response = await client.delete(
        f"/api/v1/posts/{post_id}/like",
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 404


async def test_get_like_status(client: AsyncClient, authenticated_user: dict):
    """Проверка статуса лайка"""
    # Создаём пост от другого пользователя
    unique = uuid.uuid4().hex[:8]
    reg_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": f"author5_{unique}@example.com",
            "username": f"author5_{unique}",
            "full_name": "Author",
            "password": "password123",
        },
    )
    user_id = reg_response.json()["id"]

    from app.core.security import create_verification_token

    token = create_verification_token(uuid.UUID(user_id))
    await client.get(f"/api/v1/auth/verify?token={token}")

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": f"author5_{unique}@example.com", "password": "password123"},
    )
    author_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    post_response = await client.post(
        "/api/v1/posts",
        json={"title": f"Post - {random.random()}", "content": "Content"},
        headers=author_headers,
    )
    post_id = post_response.json()["id"]

    # Проверяем статус до лайка
    status_response = await client.get(
        f"/api/v1/posts/{post_id}/like/status",
        headers=authenticated_user["headers"],
    )
    assert status_response.status_code == 200
    assert status_response.json()["liked"] is False

    # Лайкаем
    await client.post(
        f"/api/v1/posts/{post_id}/like",
        headers=authenticated_user["headers"],
    )

    # Проверяем статус после лайка
    status_response = await client.get(
        f"/api/v1/posts/{post_id}/like/status",
        headers=authenticated_user["headers"],
    )
    assert status_response.status_code == 200
    assert status_response.json()["liked"] is True
