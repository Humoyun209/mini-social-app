from httpx import AsyncClient


async def test_feed_empty(client: AsyncClient):
    """Фид работает даже когда пустой"""
    response = await client.get("/api/v1/feed")
    assert response.status_code == 200

    data = response.json()
    assert "users" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "pages" in data


async def test_feed_with_data(client: AsyncClient, authenticated_user: dict):
    """Фид содержит пользователей с постами"""
    await client.post(
        "/api/v1/posts",
        json={"title": "Feed Post", "content": "Content"},
        headers=authenticated_user["headers"],
    )

    response = await client.get("/api/v1/feed")
    assert response.status_code == 200

    data = response.json()
    assert data["total"] >= 1
    assert len(data["users"]) >= 1

    user = data["users"][0]
    assert "id" in user
    assert "email" in user
    assert "username" in user
    assert "posts" in user


async def test_feed_pagination(client: AsyncClient):
    """Пагинация фида"""
    response = await client.get("/api/v1/feed?page=1&page_size=5")
    assert response.status_code == 200

    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 5


async def test_all_endpoint(client: AsyncClient):
    """Эндпоинт /all работает как алиас"""
    response = await client.get("/api/v1/all")
    assert response.status_code == 200

    data = response.json()
    assert "users" in data
