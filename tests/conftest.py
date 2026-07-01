import os

os.environ["ENV_FILE"] = ".env.test"

import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import uuid
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_verification_token
from app.models.base import Base
from app.main import app

TEST_DB_URL = settings.DATABASE_URL


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(
        TEST_DB_URL,
        echo=False,
        poolclass=NullPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine):
    session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app, raise_app_exceptions=True)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def registered_user(client):
    """Зарегистрированный (НЕ верифицированный) пользователь"""
    unique = uuid.uuid4().hex[:8]

    user_data = {
        "email": f"test_{unique}@example.com",
        "username": f"testuser_{unique}",
        "full_name": "Test User",
        "password": "password123",
    }

    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201, f"Registration failed: {response.text}"

    data = response.json()

    assert data["is_verified"] is False

    return {
        "email": user_data["email"],
        "username": user_data["username"],
        "full_name": user_data["full_name"],
        "password": user_data["password"],
        "id": data["id"],
        "is_verified": False,
    }


@pytest_asyncio.fixture
async def verified_user(client, registered_user):
    """Верифицированный пользователь (но без токена)"""
    token = create_verification_token(uuid.UUID(registered_user["id"]))

    response = await client.get(f"/api/v1/auth/verify?token={token}")
    assert response.status_code == 200, f"Verify failed: {response.text}"

    data = response.json()

    assert data["is_verified"] is True

    return {
        **registered_user,
        "is_verified": True,
    }


@pytest_asyncio.fixture
async def authenticated_user(client, verified_user):
    """Верифицированный пользователь с токеном (может создавать посты/комментарии)"""
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": verified_user["email"],
            "password": verified_user["password"],
        },
    )
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"

    access_token = login_response.json()["access_token"]

    return {
        **verified_user,
        "access_token": access_token,
        "headers": {"Authorization": f"Bearer {access_token}"},
    }
