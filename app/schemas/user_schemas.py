from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class UserBase(BaseModel):
    """Базовая схема пользователя."""

    model_config = ConfigDict(from_attributes=True)

    username: str = Field(..., min_length=1, max_length=50)
    email: EmailStr


class UserResponse(UserBase):
    """Схема пользователя для ответа."""

    id: int


class TokenResponse(BaseModel):
    """Схема токена для ответа."""

    access_token: str
    token_type: Literal["bearer"] = "bearer"


class UserRegisterRequest(UserBase):
    """Схема регистрации пользователя."""

    password: str = Field(..., min_length=8, max_length=255)


class UserLoginRequest(UserBase):
    """Схема входа пользователя."""

    username: str | None = Field(None, min_length=1, max_length=50)
    email: EmailStr | None = None
    password: str = Field(..., min_length=8, max_length=255)

    @model_validator(mode="after")
    def check_username_or_email(self):
        """Проверяет, что указано имя пользователя или email."""
        if not self.username and not self.email:
            raise ValueError("Должно быть указано имя пользователя или email")
        return self
