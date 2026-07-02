import asyncio
import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select

from app.core.config import settings
from app.core.database import async_session_factory
from app.models.user import User
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


async def _cleanup_unverified_users() -> int:
    """
    Асинхронная функция очистки неверифицированных пользователей.

    Returns:
        int: количество удаленных пользователей
    """
    cutoff_time = datetime.now(UTC) - timedelta(hours=settings.UNVERIFIED_USER_CLEANUP_HOURS)

    async with async_session_factory() as session:
        result = await session.execute(
            select(User).where(
                User.is_verified == False,
                User.created_at < cutoff_time,
            )
        )
        users_to_delete = result.scalars().all()

        count = len(users_to_delete)

        if count > 0:
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
