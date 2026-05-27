from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Model


class BookAuthor(Model):
    """
    Модель для связи книг и авторов.

    Attributes:
        book_id (int): ID книги.
        author_id (int): ID автора.
        created_at (datetime): Дата и время создания связи.
    """

    __tablename__ = "book_authors"

    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"), primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"), ondelete="CASCADE", primary_key=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
