from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Model

from .enums import BookStatus


class UserBook(Model):
    """
    Модель для связи пользователей и книг.

    Attributes:
        user_id (int): ID пользователя.
        book_id (int): ID книги.
        status (BookStatus): Статус книги (например, "в планах", "чтение", "прочитано", "заброшено").
            По умолчанию - "в планах".
        rating (int | None): Рейтинг книги от 0 до 10.
            Может быть None, если книга не прочитана.
        added_at (datetime): Дата добавления книги на полку.
    """

    __tablename__ = "user_books"

    status: Mapped[BookStatus] = mapped_column(
        SQLAlchemyEnum(BookStatus, create_constraint=True), default=BookStatus.PLANNED
    )
    rating: Mapped[int | None] = mapped_column(default=None)
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"), primary_key=True)

    user = relationship("User", back_populates="shelf_entries")
    book = relationship("Book")
    notes = relationship("Note", back_populates="user_book", cascade="all, delete-orphan")

    __table_args__ = (CheckConstraint("rating >= 1 AND rating <= 10", name="check_rating_positive"),)
