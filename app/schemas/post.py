import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class PostBase(BaseModel):
    """Базовая схема публикации"""

    title: str = Field(..., min_length=5, max_length=255)
    content: str = Field(..., max_length=10000)


class PostCreate(PostBase):
    """Схема для создания публикации"""

    pass


class PostUpdate(BaseModel):
    """Схема для обновления публикации"""

    title: str | None = Field(None, min_length=5, max_length=255)
    content: str | None = Field(None, max_length=10000)


class PostResponse(PostBase):
    """Схема ответа с данными публикации"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    author_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    likes_count: int = 0
    comments_count: int = 0


class PostListResponse(BaseModel):
    """Схема для списка публикаций с пагинацией"""

    posts: list[PostResponse]
    total: int
    page: int
    page_size: int
    pages: int
