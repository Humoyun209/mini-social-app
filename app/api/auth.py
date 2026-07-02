from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    ResendVerificationRequest,
    TokenResponse,
)
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import (
    authenticate_user,
    register_user,
    resend_verification_email,
    verify_email,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Регистрация нового пользователя.

    После регистрации отправляется письмо с токеном верификации (в консоль).
    """
    user_data = UserCreate(**request.model_dump())
    user = await register_user(user_data, db)
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login user",
)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Аутентификация пользователя и получение JWT токена.
    """
    user = await authenticate_user(request.email, request.password, db)
    access_token = create_access_token(user.id)
    return TokenResponse(access_token=access_token)


@router.get(
    "/verify",
    response_model=UserResponse,
    summary="Verify email",
)
async def verify(
    token: str,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    user = await verify_email(token, db)
    return UserResponse.model_validate(user)


@router.post(
    "/resend-verification-email",
    response_model=UserResponse,
    summary="Resend verification email",
)
async def resend_verification(
    request: ResendVerificationRequest,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Повторная отправка письма верификации.

    Используется если пользователь не получил письмо или токен истек.
    """
    user = await resend_verification_email(request.email, db)
    return UserResponse.model_validate(user)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """
    Получение данных текущего пользователя.
    """
    return UserResponse.model_validate(current_user)
