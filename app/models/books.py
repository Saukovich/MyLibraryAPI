from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Model


class Book(Model):
    """
    Модель книги.

    Attributes:
        id (int): Идентификатор книги.
        title (str): Название книги.
        release_year (int): Год выпуска книги.
        created_at (datetime): Дата и время создания записи книги.
        authors (list): Список авторов книги.
    """

    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    title: Mapped[str] = mapped_column(String(50))
    release_year: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), init=False)

    authors = relationship("Author", secondary="book_authors", back_populates="books", lazy="selectin")

    __table_args__ = (CheckConstraint("release_year >= 0", name="release_year_check"),)
