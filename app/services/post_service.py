import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from fastapi import HTTPException, status

from app.models.post import Post
from app.models.like import Like
from app.models.comment import Comment
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate


async def get_posts(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 10,
    search: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> tuple[list[Post], int]:
    """
    Получение списка публикаций с пагинацией, поиском и фильтрацией.

    Args:
        db: сессия БД
        page: номер страницы
        page_size: размер страницы
        search: поиск по title/content
        date_from: фильтр по дате создания (от)
        date_to: фильтр по дате создания (до)

    Returns:
        tuple: (список публикаций, общее количество)
    """
    # Базовый запрос
    query = select(Post)

    # Поиск
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                Post.title.ilike(search_pattern),
                Post.content.ilike(search_pattern),
            )
        )

    # Фильтрация по дате
    if date_from:
        query = query.where(Post.created_at >= date_from)
    if date_to:
        query = query.where(Post.created_at <= date_to)

    # Общее количество
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Пагинация
    offset = (page - 1) * page_size
    query = query.order_by(Post.created_at.desc()).offset(offset).limit(page_size)

    result = await db.execute(query)
    posts = result.scalars().all()

    return posts, total


async def get_post(post_id: uuid.UUID, db: AsyncSession) -> Post:
    """
    Получение публикации по ID.

    Args:
        post_id: ID публикации
        db: сессия БД

    Returns:
        Post: публикация

    Raises:
        HTTPException: если публикация не найдена
    """
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    return post


async def create_post(
    post_data: PostCreate,
    author: User,
    db: AsyncSession,
) -> Post:
    """
    Создание новой публикации.

    Args:
        post_data: данные для создания
        author: автор публикации
        db: сессия БД

    Returns:
        Post: созданная публикация
    """
    post = Post(
        title=post_data.title,
        content=post_data.content,
        author_id=author.id,
    )

    db.add(post)
    await db.flush()
    await db.refresh(post)

    return post


async def update_post(
    post_id: uuid.UUID,
    post_data: PostUpdate,
    current_user: User,
    db: AsyncSession,
) -> Post:
    """
    Обновление публикации.

    Args:
        post_id: ID публикации
        post_data: данные для обновления
        current_user: текущий пользователь
        db: сессия БД

    Returns:
        Post: обновленная публикация

    Raises:
        HTTPException: если публикация не найдена или нет прав
    """
    post = await get_post(post_id, db)

    # Проверяем что пользователь - автор
    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own posts",
        )

    # Обновляем поля
    update_data = post_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)

    await db.flush()
    await db.refresh(post)

    return post


async def delete_post(
    post_id: uuid.UUID,
    current_user: User,
    db: AsyncSession,
) -> None:
    """
    Удаление публикации.

    Args:
        post_id: ID публикации
        current_user: текущий пользователь
        db: сессия БД

    Raises:
        HTTPException: если публикация не найдена или нет прав
    """
    post = await get_post(post_id, db)

    # Проверяем что пользователь - автор
    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own posts",
        )

    await db.delete(post)
    await db.flush()


async def get_post_with_counts(post: Post, db: AsyncSession) -> dict:
    """
    Получение публикации с количеством лайков и комментариев.

    Args:
        post: публикация
        db: сессия БД

    Returns:
        dict: данные публикации с counts
    """
    # Количество лайков
    likes_count_result = await db.execute(
        select(func.count()).select_from(Like).where(Like.post_id == post.id)
    )
    likes_count = likes_count_result.scalar() or 0

    # Количество комментариев
    comments_count_result = await db.execute(
        select(func.count()).select_from(Comment).where(Comment.post_id == post.id)
    )
    comments_count = comments_count_result.scalar() or 0

    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "author_id": post.author_id,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
        "likes_count": likes_count,
        "comments_count": comments_count,
    }
