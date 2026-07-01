import random
import uuid
import pytest
from httpx import AsyncClient


async def test_unverified_cannot_create_post(client: AsyncClient, registered_user: dict):
    """Неверифицированный не может создать пост"""
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    assert login_response.status_code == 200
    response = await client.post(
        "/api/v1/posts",
        json={"title": "Test", "content": "Content"},
    )
    assert response.status_code == 401


async def test_unauthenticated_cannot_create_post(client: AsyncClient):
    """Без токена нельзя создать пост"""
    response = await client.post(
        "/api/v1/posts",
        json={"title": "Test", "content": "Content"},
    )
    assert response.status_code == 401


async def test_unauthenticated_cannot_create_comment(client: AsyncClient):
    """Без токена нельзя создать комментарий"""
    response = await client.post(
        "/api/v1/posts/00000000-0000-0000-0000-000000000000/comments",
        json={"content": "Test"},
    )
    assert response.status_code == 401


async def test_unauthenticated_cannot_like(client: AsyncClient):
    """Без токена нельзя лайкать"""
    response = await client.post(
        "/api/v1/posts/00000000-0000-0000-0000-000000000000/like",
    )
    assert response.status_code == 401


async def test_anyone_can_view_posts(client: AsyncClient):
    """Посты может смотреть любой (без токена)"""
    response = await client.get("/api/v1/posts")
    assert response.status_code == 200


async def test_anyone_can_view_feed(client: AsyncClient):
    """Фид может смотреть любой (без токена)"""
    response = await client.get("/api/v1/feed")
    assert response.status_code == 200


async def test_anyone_can_view_post(client: AsyncClient, authenticated_user: dict):
    """Конкретный пост может смотреть любой"""
    post_response = await client.post(
        "/api/v1/posts",
        json={"title": "Public Post", "content": "Content"},
        headers=authenticated_user["headers"],
    )
    post_id = post_response.json()["id"]

    response = await client.get(f"/api/v1/posts/{post_id}")
    assert response.status_code == 200


async def test_anyone_can_view_comments(client: AsyncClient, authenticated_user: dict):
    """Комментарии может смотреть любой"""
    post_response = await client.post(
        "/api/v1/posts",
        json={"title": f"Post {random.random()}", "content": "Content"},
        headers=authenticated_user["headers"],
    )
    post_id = post_response.json()["id"]

    response = await client.get(f"/api/v1/posts/{post_id}/comments")
    assert response.status_code == 200
