import uuid
import math
from datetime import datetime
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_verified_user
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate, PostResponse, PostListResponse
from app.services.post_service import (
    get_posts,
    get_post,
    create_post,
    update_post,
    delete_post,
    get_post_with_counts,
)

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get(
    "",
    response_model=PostListResponse,
    summary="Get posts list",
)
async def list_posts(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    search: str | None = Query(None, description="Search by title or content"),
    date_from: datetime | None = Query(None, description="Filter by date from"),
    date_to: datetime | None = Query(None, description="Filter by date to"),
    db: AsyncSession = Depends(get_db),
) -> PostListResponse:
    """
    Получение списка публикаций с пагинацией, поиском и фильтрацией.

    Доступно всем пользователям (включая неверифицированных).
    """
    posts, total = await get_posts(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        date_from=date_from,
        date_to=date_to,
    )

    posts_with_counts = []
    for post in posts:
        post_data = await get_post_with_counts(post, db)
        posts_with_counts.append(PostResponse(**post_data))

    pages = math.ceil(total / page_size) if total > 0 else 0

    return PostListResponse(
        posts=posts_with_counts,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.post(
    "",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create post",
)
async def create_new_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db),
) -> PostResponse:
    """
    Создание новой публикации.

    Доступно только верифицированным пользователям.
    """
    post = await create_post(post_data, current_user, db)
    post_data_with_counts = await get_post_with_counts(post, db)
    return PostResponse(**post_data_with_counts)


@router.get(
    "/{post_id}",
    response_model=PostResponse,
    summary="Get post by ID",
)
async def get_post_by_id(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> PostResponse:
    """
    Получение публикации по ID.

    Доступно всем пользователям.
    """
    post = await get_post(post_id, db)
    post_data = await get_post_with_counts(post, db)
    return PostResponse(**post_data)


@router.patch(
    "/{post_id}",
    response_model=PostResponse,
    summary="Update post",
)
async def update_post_by_id(
    post_id: uuid.UUID,
    post_data: PostUpdate,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db),
) -> PostResponse:
    """
    Обновление публикации.

    Доступно только автору публикации (верифицированному).
    """
    post = await update_post(post_id, post_data, current_user, db)
    post_data_with_counts = await get_post_with_counts(post, db)
    return PostResponse(**post_data_with_counts)


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete post",
)
async def delete_post_by_id(
    post_id: uuid.UUID,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Удаление публикации.

    Доступно только автору публикации (верифицированному).
    """
    await delete_post(post_id, current_user, db)
