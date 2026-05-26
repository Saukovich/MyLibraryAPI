from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, validates

from app.core.database import Model


class Book(Model):
    """
    Модель книги.

    Attributes:
        id (int): Идентификатор книги.
        title (str): Название книги.
        release_year (int): Год выпуска книги.
        created_at (datetime): Дата и время создания записи книги.
    """

    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    release_year: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    @validates("title")
    def validate_title(self, key: str, value: str) -> str:
        """
        Валидация названия книги.
        :param key: str - Атрибут, который валидируется
        :param value: str - Значение названия книги
        :return: str - Значение названия книги
        """
        if value is None:
            raise ValueError("Title is required")
        if len(value) > 50:
            raise ValueError("Title must be less than 50 characters")
        return value

    @validates("release_year")
    def validate_release_year(self, key: str, value: int) -> int:
        """
        Валидация года выпуска книги.
        :param key: str - Атрибут, который валидируется
        :param value: int - Значение года выпуска книги
        :return: int - Значение года выпуска книги
        """
        if value is None:
            raise ValueError("Release year is required")
        if value <= 0:
            raise ValueError("Release year must be greater than 0")
        return value
