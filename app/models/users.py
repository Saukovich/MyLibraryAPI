from datetime import datetime, timezone

from email_validator import EmailNotValidError, validate_email
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, validates

from app.core.database import Model


class User(Model):
    """
    Модель пользователя.

    Attributes:
        id (int): Идентификатор пользователя.
        username (str): Имя пользователя.
        email (str): Электронная почта пользователя.
        password (str): Хеш пароля пользователя.
        created_at (DateTime): Дата и время создания пользователя.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    @validates("username")
    def validate_username(self, key: str, value: str) -> str:
        """
        Валидация имени пользователя.
        :param key: str - Атрибут, который валидируется
        :param value: str - Значение имени пользователя
        :return: str - Значение имени пользователя
        """
        if value is None:
            raise ValueError("Username is required.")
        if len(value) < 5:
            raise ValueError("Username must be greater or equal than 5 characters.")
        if len(value) > 50:
            raise ValueError("Username must be less than 50 characters.")
        return value

    @validates("email")
    def validate_email(self, key: str, value: str) -> str:
        """
        Валидация электронной почты пользователя.
        :param key: str - Атрибут, который валидируется
        :param value: str - Значение электронной почты пользователя
        :return: str - Значение электронной почты пользователя
        """
        if value is None:
            raise ValueError("Email is required.")
        try:
            email_info = validate_email(value)
            email = email_info.normalized
            if len(email) > 100:
                raise ValueError("Email must be less than 100 characters.")
            self.__dict__[key] = email
            return value
        except EmailNotValidError:
            raise ValueError("Invalid email address.")
        except ValueError:
            raise ValueError("Email must be less than 100 characters.")

    @validates("password")
    def validate_password(self, key: str, value: str) -> str:
        """
        Валидация пароля пользователя.
        :param key: str - Атрибут, который валидируется
        :param value: str - Значение хэша пароля пользователя
        :return: str - Значение хэша пароля пользователя
        """
        if value is None or len(value) == 0:
            raise ValueError("Password is required.")
        if len(value) > 255:
            raise ValueError("Password must be less than 255 characters.")
        return value
