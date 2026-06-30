import logging

logger = logging.getLogger(__name__)


async def send_verification_email(to_email: str, verification_token: str) -> None:
    """
    Отправка письма с токеном верификации email (console mode).
    """
    logger.info("=" * 80)
    logger.info("VERIFICATION EMAIL (CONSOLE MODE)")
    logger.info("=" * 80)
    logger.info(f"To: {to_email}")
    logger.info(f"Verification Token: {verification_token}")
    logger.info(
        f"Verification Link: http://localhost:8000/api/v1/auth/verify?token={verification_token}"
    )
    logger.info("=" * 80)
