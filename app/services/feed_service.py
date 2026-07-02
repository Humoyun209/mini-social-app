from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Post, User


async def get_feed(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 10,
) -> tuple[list[User], int]:
    """
    Получение фида: пользователи с их публикациями и лайками.

    Args:
        db: сессия БД
        page: номер страницы
        page_size: размер страницы

    Returns:
        tuple: (список пользователей, общее количество)
    """
    count_query = select(func.count()).select_from(User)
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    offset = (page - 1) * page_size

    query = (
        select(User)
        .options(selectinload(User.posts).selectinload(Post.likes))
        .order_by(User.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )

    result = await db.execute(query)
    users = result.scalars().unique().all()

    return users, total
