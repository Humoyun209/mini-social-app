import random
import uuid

from httpx import AsyncClient


async def test_create_comment(client: AsyncClient, authenticated_user: dict):
    """Верифицированный пользователь может создать комментарий"""
    post_response = await client.post(
        "/api/v1/posts",
        json={"title": "Post for Comments", "content": "Content"},
        headers=authenticated_user["headers"],
    )
    post_id = post_response.json()["id"]

    response = await client.post(
        f"/api/v1/posts/{post_id}/comments",
        json={"content": "Great post!"},
        headers=authenticated_user["headers"],
    )

    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "Great post!"
    assert data["post_id"] == post_id
    assert data["author_id"] == authenticated_user["id"]


async def test_create_comment_to_nonexistent_post(client: AsyncClient, authenticated_user: dict):
    """Нельзя создать комментарий к несуществующему посту"""
    fake_id = uuid.uuid4()
    response = await client.post(
        f"/api/v1/posts/{fake_id}/comments",
        json={"content": "Comment"},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 404


async def test_create_comment_unauthenticated(client: AsyncClient):
    """Без токена нельзя создать комментарий"""
    response = await client.post(
        "/api/v1/posts/00000000-0000-0000-0000-000000000000/comments",
        json={"content": "Comment"},
    )
    assert response.status_code == 401


async def test_list_comments(client: AsyncClient, authenticated_user: dict):
    """Список комментариев к посту"""
    post_response = await client.post(
        "/api/v1/posts",
        json={"title": f"Post - {random.random()}", "content": "Content"},
        headers=authenticated_user["headers"],
    )
    post_id = post_response.json()["id"]

    for i in range(3):
        await client.post(
            f"/api/v1/posts/{post_id}/comments",
            json={"content": f"Comment {i}"},
            headers=authenticated_user["headers"],
        )

    response = await client.get(f"/api/v1/posts/{post_id}/comments")
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 3
    assert len(data["comments"]) == 3


async def test_delete_comment(client: AsyncClient, authenticated_user: dict):
    """Автор может удалить свой комментарий"""
    # Создаём пост и комментарий
    post_response = await client.post(
        "/api/v1/posts",
        json={"title": f"Post - {random.random()}", "content": "Content"},
        headers=authenticated_user["headers"],
    )

    print("New Post Response", post_response.json())
    post_id = post_response.json()["id"]

    comment_response = await client.post(
        f"/api/v1/posts/{post_id}/comments",
        json={"content": "To delete"},
        headers=authenticated_user["headers"],
    )
    comment_id = comment_response.json()["id"]

    response = await client.delete(
        f"/api/v1/comments/{comment_id}",
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 204


async def test_delete_comment_not_found(client: AsyncClient, authenticated_user: dict):
    """Удаление несуществующего комментария — 404"""
    fake_id = uuid.uuid4()
    response = await client.delete(
        f"/api/v1/comments/{fake_id}",
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 404


async def test_list_comments_nonexistent_post(client: AsyncClient):
    """Список комментариев к несуществующему посту — 404"""
    fake_id = uuid.uuid4()
    response = await client.get(f"/api/v1/posts/{fake_id}/comments")
    assert response.status_code == 404
