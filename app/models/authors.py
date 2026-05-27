from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Model


class Author(Model):
    """
    Модель автора

    Attributes:
        id (int): Идентификатор автора.
        fullname (str): Полное имя автора.
        birth_year (int): Год рождения автора.
        death_year (int | None): Год смерти автора (None, если автор жив).
        created_at (datetime): Дата и время создания записи.
        books (list[Book]): Список книг, написанных данным автором.
            Связь с моделью Book через промежуточную таблицу book_authors.
    """

    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    fullname: Mapped[str] = mapped_column(String(100))
    birth_year: Mapped[int] = mapped_column()
    death_year: Mapped[int | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))

    books = relationship("Book", secondary="book_authors", back_populates="authors")

    __table_args__ = (
        CheckConstraint("birth_year >= 0", name="check_birth_year"),
        CheckConstraint("death_year >= 0", name="check_death_year"),
        CheckConstraint("birth_year <= death_year", name="check_birth_year_death_year"),
    )
