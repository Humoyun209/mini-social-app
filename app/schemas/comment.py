import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CommentBase(BaseModel):
    """Базовая схема комментария"""

    content: str = Field(..., max_length=2000)


class CommentCreate(CommentBase):
    """Схема для создания комментария"""

    pass


class CommentResponse(CommentBase):
    """Схема ответа с данными комментария"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    post_id: uuid.UUID
    author_id: uuid.UUID
    created_at: datetime


class CommentListResponse(BaseModel):
    """Схема для списка комментариев"""

    comments: list[CommentResponse]
    total: int
