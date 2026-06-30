from datetime import datetime, timedelta
import uuid

import bcrypt
import jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    """Хеширование пароля"""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    plain_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(plain_bytes, hashed_bytes)


def create_access_token(user_id: uuid.UUID) -> str:
    """Создание JWT токена доступа"""
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_verification_token(user_id: uuid.UUID) -> str:
    """Создание токена для верификации email"""
    expire = datetime.utcnow() + timedelta(hours=settings.VERIFICATION_TOKEN_EXPIRE_HOURS)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "verification",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str, token_type: str = "access") -> dict:
    """
    Декодирование JWT токена

    Args:
        token: JWT токен
        token_type: ожидаемый тип токена ("access" или "verification")

    Returns:
        dict с payload токена

    Raises:
        jwt.ExpiredSignatureError: токен истек
        jwt.InvalidTokenError: невалидный токен
        ValueError: неверный тип токена
    """
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    if payload.get("type") != token_type:
        raise ValueError(f"Invalid token type: expected {token_type}")

    return payload
