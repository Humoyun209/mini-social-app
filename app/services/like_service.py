import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.like import Like
from app.models.post import Post
from app.models.user import User


async def like_post(
    post_id: uuid.UUID,
    current_user: User,
    db: AsyncSession,
) -> Like:
    """
    Поставить лайк публикации.

    Args:
        post_id: ID публикации
        current_user: текущий пользователь
        db: сессия БД

    Returns:
        Like: созданный лайк

    Raises:
        HTTPException: если публикация не найдена, это свой пост или уже лайкал
    """
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    if post.author_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot like your own post",
        )

    result = await db.execute(
        select(Like).where(
            Like.user_id == current_user.id,
            Like.post_id == post_id,
        )
    )
    existing_like = result.scalar_one_or_none()

    if existing_like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already liked this post",
        )

    like = Like(
        user_id=current_user.id,
        post_id=post_id,
    )

    db.add(like)
    await db.flush()
    await db.refresh(like)

    return like


async def unlike_post(
    post_id: uuid.UUID,
    current_user: User,
    db: AsyncSession,
) -> None:
    """
    Убрать лайк с публикации.

    Args:
        post_id: ID публикации
        current_user: текущий пользователь
        db: сессия БД

    Raises:
        HTTPException: если публикация не найдена или лайк не найден
    """
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    result = await db.execute(
        select(Like).where(
            Like.user_id == current_user.id,
            Like.post_id == post_id,
        )
    )
    like = result.scalar_one_or_none()

    if not like:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Like not found",
        )

    await db.delete(like)
    await db.flush()


async def get_like_status(
    post_id: uuid.UUID,
    current_user: User,
    db: AsyncSession,
) -> dict:
    """
    Получить статус лайка пользователя для публикации.

    Args:
        post_id: ID публикации
        current_user: текущий пользователь
        db: сессия БД

    Returns:
        dict: статус лайка (liked, like_id)
    """
    result = await db.execute(
        select(Like).where(
            Like.user_id == current_user.id,
            Like.post_id == post_id,
        )
    )
    like = result.scalar_one_or_none()

    return {
        "liked": like is not None,
        "like_id": like.id if like else None,
    }
