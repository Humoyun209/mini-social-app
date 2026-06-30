from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    """Запрос на регистрацию"""

    email: EmailStr
    username: str
    full_name: str
    password: str


class LoginRequest(BaseModel):
    """Запрос на вход"""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Ответ с токеном"""

    access_token: str
    token_type: str = "bearer"


class VerifyEmailRequest(BaseModel):
    """Запрос на верификацию email"""

    token: str


class ResendVerificationRequest(BaseModel):
    """Запрос на повторную отправку письма верификации"""

    email: EmailStr
