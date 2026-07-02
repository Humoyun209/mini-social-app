from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_verification_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.email_service import send_verification_email


async def register_user(user_data: UserCreate, db: AsyncSession) -> User:
    """
    Регистрация нового пользователя

    Args:
        user_data: данные для регистрации
        db: сессия БД

    Returns:
        User: созданный пользователь

    Raises:
        HTTPException: если email или username уже заняты
    """
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        password_hash=hash_password(user_data.password),
        is_verified=False,
    )

    db.add(user)
    await db.flush()
    await db.refresh(user)

    verification_token = create_verification_token(user.id)

    await send_verification_email(user.email, verification_token)

    return user


async def authenticate_user(email: str, password: str, db: AsyncSession) -> User:
    """
    Аутентификация пользователя

    Args:
        email: email пользователя
        password: пароль
        db: сессия БД

    Returns:
        User: аутентифицированный пользователь

    Raises:
        HTTPException: если неверные credentials
    """
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return user


async def verify_email(token: str, db: AsyncSession) -> User:
    """
    Верификация email по токену

    Args:
        token: токен верификации
        db: сессия БД

    Returns:
        User: верифицированный пользователь

    Raises:
        HTTPException: если токен невалидный или пользователь не найден
    """
    import jwt

    from app.core.security import decode_token

    try:
        payload = decode_token(token, token_type="verification")
        user_id = UUID(payload["sub"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token",
        )
    except (ValueError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token payload",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified",
        )

    user.is_verified = True
    await db.flush()
    await db.refresh(user)

    return user


async def resend_verification_email(email: str, db: AsyncSession) -> User:
    """
    Повторная отправка письма верификации.

    Args:
        email: email пользователя
        db: сессия БД

    Returns:
        User: пользователь

    Raises:
        HTTPException: если пользователь не найден или уже верифицирован
    """
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified",
        )

    verification_token = create_verification_token(user.id)

    await send_verification_email(user.email, verification_token)

    return user
