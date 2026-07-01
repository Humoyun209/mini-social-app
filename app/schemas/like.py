import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class LikeResponse(BaseModel):
    """Схема ответа с данными лайка"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    post_id: uuid.UUID
    created_at: datetime


class LikeStatusResponse(BaseModel):
    """Схема ответа со статусом лайка"""

    liked: bool
    like_id: uuid.UUID | None = None
