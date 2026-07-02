import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FeedLikeResponse(BaseModel):
    """Лайк в фиде"""

    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID
    post_id: uuid.UUID
    created_at: datetime


class FeedPostResponse(BaseModel):
    """Публикация в фиде"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    likes: list[FeedLikeResponse] = []


class FeedUserResponse(BaseModel):
    """Пользователь в фиде"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    username: str
    full_name: str
    is_verified: bool
    created_at: datetime
    posts: list[FeedPostResponse] = []


class FeedResponse(BaseModel):
    """Ответ фида"""

    users: list[FeedUserResponse]
    total: int
    page: int
    page_size: int
    pages: int
