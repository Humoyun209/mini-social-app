import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.like import LikeResponse, LikeStatusResponse
from app.services.like_service import like_post, unlike_post, get_like_status

router = APIRouter(tags=["Likes"])


@router.post(
    "/posts/{post_id}/like",
    response_model=LikeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Like post",
)
async def like_post_endpoint(
    post_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LikeResponse:
    """
    Поставить лайк публикации.

    Доступно всем аутентифицированным пользователям (включая неверифицированных).

    Ограничения:
    - Нельзя лайкать свою публикацию
    - Один лайк на публикацию от пользователя
    """
    like = await like_post(post_id, current_user, db)
    return LikeResponse.model_validate(like)


@router.delete(
    "/posts/{post_id}/like",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unlike post",
)
async def unlike_post_endpoint(
    post_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Убрать лайк с публикации.

    Доступно всем аутентифицированным пользователям.
    """
    await unlike_post(post_id, current_user, db)


@router.get(
    "/posts/{post_id}/like/status",
    response_model=LikeStatusResponse,
    summary="Get like status",
)
async def get_like_status_endpoint(
    post_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LikeStatusResponse:
    """
    Получить статус лайка пользователя для публикации.

    Возвращает информацию о том, лайкнул ли пользователь данную публикацию.
    """
    status_data = await get_like_status(post_id, current_user, db)
    return LikeStatusResponse(**status_data)
