from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, validates

from app.core.database import Model

from .enums import BookStatus


class UserBook(Model):
    """
    Модель для связи пользователей и книг.

    Attributes:
        user_id (int): ID пользователя.
        book_id (int): ID книги.
        status (BookStatus): Статус книги (например, "planned", "reading", "read").
            По умолчанию - "planned".
        rating (int | None): Рейтинг книги от 0 до 10.
            Может быть None, если книга не прочитана.
        added_at (datetime): Дата добавления книги на полку.
    """

    __tablename__ = "user_books"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), primary_key=True)
    status: Mapped[BookStatus] = mapped_column(
        SQLAlchemyEnum(BookStatus, create_constraint=True), default=BookStatus.PLANNED, nullable=False
    )
    rating: Mapped[int | None] = mapped_column(default=None, nullable=True)
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    @validates("rating")
    def validate_rating(self, key: str, value: int | None) -> int | None:
        """
        Валидация рейтинга книги.
        :param key: str - Атрибут, который валидируется.
        :param value: int | None - Значение рейтинга.
        :return: int | None - Значение рейтинга.
        """
        if value is not None and not 0 <= value <= 10:
            raise ValueError("Rating must be between 0 and 10")
        return value
