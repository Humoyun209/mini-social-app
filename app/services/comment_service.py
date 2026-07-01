import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status

from app.models.comment import Comment
from app.models.post import Post
from app.models.user import User
from app.schemas.comment import CommentCreate


async def get_comments_by_post(
    post_id: uuid.UUID,
    db: AsyncSession,
) -> tuple[list[Comment], int]:
    """
    Получение списка комментариев к публикации.

    Args:
        post_id: ID публикации
        db: сессия БД

    Returns:
        tuple: (список комментариев, общее количество)
    """
    # Проверяем что пост существует
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    query = select(Comment).where(Comment.post_id == post_id)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Comment.created_at.asc())
    result = await db.execute(query)
    comments = result.scalars().all()

    return comments, total


async def create_comment(
    post_id: uuid.UUID,
    comment_data: CommentCreate,
    author: User,
    db: AsyncSession,
) -> Comment:
    """
    Создание нового комментария.

    Args:
        post_id: ID публикации
        comment_data: данные для создания
        author: автор комментария
        db: сессия БД

    Returns:
        Comment: созданный комментарий

    Raises:
        HTTPException: если публикация не найдена
    """
    # Проверяем что пост существует
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    comment = Comment(
        post_id=post_id,
        author_id=author.id,
        content=comment_data.content,
    )

    db.add(comment)
    await db.flush()
    await db.refresh(comment)

    return comment


async def delete_comment(
    comment_id: uuid.UUID,
    current_user: User,
    db: AsyncSession,
) -> None:
    """
    Удаление комментария.

    Args:
        comment_id: ID комментария
        current_user: текущий пользователь
        db: сессия БД

    Raises:
        HTTPException: если комментарий не найден или нет прав
    """
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    # Проверяем что пользователь - автор
    if comment.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own comments",
        )

    await db.delete(comment)
    await db.flush()
