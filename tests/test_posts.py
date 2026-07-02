import uuid
from datetime import datetime, timedelta

from httpx import AsyncClient


async def test_create_post(client: AsyncClient, authenticated_user: dict):
    """Верифицированный пользователь может создать пост"""
    post_data = {
        "title": "Test Post Title",
        "content": "This is test content for the post.",
    }

    response = await client.post(
        "/api/v1/posts",
        json=post_data,
        headers=authenticated_user["headers"],
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == post_data["title"]
    assert data["content"] == post_data["content"]
    assert data["author_id"] == authenticated_user["id"]
    assert "id" in data
    assert "created_at" in data


async def test_create_post_unauthenticated(client: AsyncClient):
    """Без токена нельзя создать пост"""
    post_data = {"title": "Test", "content": "Content"}

    response = await client.post("/api/v1/posts", json=post_data)
    assert response.status_code == 401


async def test_create_post_short_title(client: AsyncClient, authenticated_user: dict):
    """Заголовок должен быть минимум 5 символов"""
    post_data = {"title": "Hi!", "content": "Content"}

    response = await client.post(
        "/api/v1/posts",
        json=post_data,
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 422


async def test_list_posts(client: AsyncClient, authenticated_user: dict):
    """Список постов с пагинацией"""
    for i in range(3):
        await client.post(
            "/api/v1/posts",
            json={"title": f"Post {i}", "content": f"Content {i}"},
            headers=authenticated_user["headers"],
        )

    response = await client.get("/api/v1/posts?page=1&page_size=10")
    assert response.status_code == 200

    data = response.json()
    assert "posts" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "pages" in data
    assert data["total"] >= 3


async def test_list_posts_pagination(client: AsyncClient, authenticated_user: dict):
    """Пагинация работает корректно"""
    for i in range(5):
        await client.post(
            "/api/v1/posts",
            json={"title": f"Post {i}", "content": f"Content {i}"},
            headers=authenticated_user["headers"],
        )

    response = await client.get("/api/v1/posts?page=1&page_size=2")
    data = response.json()

    assert len(data["posts"]) == 2
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["total"] >= 5
    assert data["pages"] >= 3


async def test_list_posts_search(client: AsyncClient, authenticated_user: dict):
    """Поиск по title/content"""
    await client.post(
        "/api/v1/posts",
        json={"title": "Unique Python Title", "content": "Some content"},
        headers=authenticated_user["headers"],
    )

    response = await client.get("/api/v1/posts?search=Python")
    data = response.json()

    assert data["total"] >= 1
    assert any("Python" in p["title"] for p in data["posts"])


async def test_list_posts_date_filter(client: AsyncClient, authenticated_user: dict):
    """Фильтрация по дате"""
    await client.post(
        "/api/v1/posts",
        json={"title": "Recent Post", "content": "Content"},
        headers=authenticated_user["headers"],
    )

    date_from = (datetime.now() - timedelta(hours=1)).isoformat()
    response = await client.get(f"/api/v1/posts?date_from={date_from}")
    data = response.json()

    assert response.status_code == 200

    assert data["total"] >= 1


async def test_get_post_by_id(client: AsyncClient, authenticated_user: dict):
    """Получение поста по ID"""
    create_response = await client.post(
        "/api/v1/posts",
        json={"title": "My Post", "content": "My Content"},
        headers=authenticated_user["headers"],
    )
    post_id = create_response.json()["id"]

    response = await client.get(f"/api/v1/posts/{post_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == post_id
    assert data["title"] == "My Post"
    assert "likes_count" in data
    assert "comments_count" in data


async def test_get_post_not_found(client: AsyncClient):
    """Пост не найден — 404"""
    fake_id = uuid.uuid4()
    response = await client.get(f"/api/v1/posts/{fake_id}")
    assert response.status_code == 404


async def test_update_post(client: AsyncClient, authenticated_user: dict):
    """Автор может обновить свой пост"""
    create_response = await client.post(
        "/api/v1/posts",
        json={"title": "Original Title", "content": "Original Content"},
        headers=authenticated_user["headers"],
    )
    post_id = create_response.json()["id"]

    response = await client.patch(
        f"/api/v1/posts/{post_id}",
        json={"title": "Updated Title"},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"
    assert response.json()["content"] == "Original Content"


async def test_delete_post(client: AsyncClient, authenticated_user: dict):
    """Автор может удалить свой пост"""
    create_response = await client.post(
        "/api/v1/posts",
        json={"title": "To Delete", "content": "Content"},
        headers=authenticated_user["headers"],
    )
    post_id = create_response.json()["id"]

    response = await client.delete(
        f"/api/v1/posts/{post_id}",
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 204

    get_response = await client.get(f"/api/v1/posts/{post_id}")
    assert get_response.status_code == 404


async def test_delete_post_not_found(client: AsyncClient, authenticated_user: dict):
    """Удаление несуществующего поста — 404"""
    fake_id = uuid.uuid4()
    response = await client.delete(
        f"/api/v1/posts/{fake_id}",
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 404
