from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now(timezone.utc))

    shelf_entries = relationship("UserBook", back_populates="user")
