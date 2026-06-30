import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """Базовая схема пользователя"""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_]+$")
    full_name: str = Field(..., min_length=2, max_length=100)


class UserCreate(UserBase):
    """Схема для создания пользователя"""

    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""

    username: str | None = Field(None, min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_]+$")
    full_name: str | None = Field(None, min_length=2, max_length=100)


class UserResponse(UserBase):
    """Схема ответа с данными пользователя"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class UserInDB(UserResponse):
    """Пользователь в БД (с хешем пароля)"""

    password_hash: str
