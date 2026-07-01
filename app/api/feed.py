import math
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.feed import FeedResponse, FeedUserResponse
from app.services.feed_service import get_feed

router = APIRouter(tags=["Feed"])


@router.get(
    "/feed",
    response_model=FeedResponse,
    summary="Get feed",
)
@router.get(
    "/all",
    response_model=FeedResponse,
    summary="Get all users with posts and likes",
    include_in_schema=False,
)
async def get_feed_endpoint(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    db: AsyncSession = Depends(get_db),
) -> FeedResponse:
    """
    Получение фида: список пользователей с их публикациями и лайками.

    Доступно всем (без аутентификации).

    Структура ответа:
    - Пользователи
      - Публикации
        - Лайки
    """
    users, total = await get_feed(db, page=page, page_size=page_size)

    feed_users = [FeedUserResponse.model_validate(user) for user in users]

    pages = math.ceil(total / page_size) if total > 0 else 0

    return FeedResponse(
        users=feed_users,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )
