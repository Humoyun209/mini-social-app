import asyncio
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, delete

from app.tasks.celery_app import celery_app
from app.core.database import async_session_factory
from app.models.user import User
from app.core.config import settings

logger = logging.getLogger(__name__)


async def _cleanup_unverified_users() -> int:
    """
    Асинхронная функция очистки неверифицированных пользователей.

    Returns:
        int: количество удаленных пользователей
    """
    cutoff_time = datetime.now(timezone.utc) - timedelta(
        hours=settings.UNVERIFIED_USER_CLEANUP_HOURS
    )

    async with async_session_factory() as session:
        # Находим пользователей для удаления
        result = await session.execute(
            select(User).where(
                User.is_verified == False,
                User.created_at < cutoff_time,
            )
        )
        users_to_delete = result.scalars().all()

        count = len(users_to_delete)

        if count > 0:
            # Удаляем пользователей
            await session.execute(
                delete(User).where(
                    User.is_verified == False,
                    User.created_at < cutoff_time,
                )
            )
            await session.commit()
            logger.info(f"Deleted {count} unverified users older than {cutoff_time}")
        else:
            logger.info("No unverified users to delete")

        return count


@celery_app.task(
    name="cleanup_unverified_users",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def cleanup_unverified_users(self) -> dict:
    """
    Celery задача для очистки неверифицированных пользователей.

    Удаляет пользователей с is_verified=False, которые были созданы
    более UNVERIFIED_USER_CLEANUP_HOURS часов назад.

    Returns:
        dict: результат выполнения задачи
    """
    try:
        logger.info("Starting cleanup of unverified users...")
        count = asyncio.run(_cleanup_unverified_users())

        return {
            "status": "success",
            "deleted_count": count,
            "cutoff_hours": settings.UNVERIFIED_USER_CLEANUP_HOURS,
        }
    except Exception as exc:
        logger.error(f"Error cleaning up unverified users: {exc}")
        raise self.retry(exc=exc)
