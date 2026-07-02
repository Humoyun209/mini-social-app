import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_verified_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentListResponse, CommentResponse
from app.services.comment_service import (
    create_comment,
    delete_comment,
    get_comments_by_post,
)

router = APIRouter(tags=["Comments"])


@router.get(
    "/posts/{post_id}/comments",
    response_model=CommentListResponse,
    summary="Get comments for post",
)
async def list_comments(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> CommentListResponse:
    """
    Получение списка комментариев к публикации.

    Доступно всем пользователям.
    """
    comments, total = await get_comments_by_post(post_id, db)

    return CommentListResponse(
        comments=[CommentResponse.model_validate(comment) for comment in comments],
        total=total,
    )


@router.post(
    "/posts/{post_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create comment",
)
async def create_new_comment(
    post_id: uuid.UUID,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db),
) -> CommentResponse:
    """
    Создание нового комментария к публикации.

    Доступно только верифицированным пользователям.
    """
    comment = await create_comment(post_id, comment_data, current_user, db)
    return CommentResponse.model_validate(comment)


@router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete comment",
)
async def delete_comment_by_id(
    comment_id: uuid.UUID,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Удаление комментария.

    Доступно только автору комментария (верифицированному).
    """
    await delete_comment(comment_id, current_user, db)
