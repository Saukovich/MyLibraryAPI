from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, ForeignKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Model


class Note(Model):
    """
    Модель заметки.

    Attributes:
        id (int): Идентификатор заметки.
        text (str): Текст заметки.
        page (int): Номер страницы, на которой сделана заметка.
        created_at (datetime): Дата и время создания заметки.
        user_id (int): Идентификатор пользователя.
        book_id (int): Идентификатор книги.
        shelf_entry (UserBook): Связь с пользовательской книгой.
    """

    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    text: Mapped[str] = mapped_column()
    page: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))

    user_id: Mapped[int] = mapped_column()
    book_id: Mapped[int] = mapped_column()

    shelf_entry = relationship("UserBook", back_populates="notes")

    __table_args__ = (
        CheckConstraint("page > 0"),
        ForeignKeyConstraint(["user_id", "book_id"], ["user_books.user_id", "user_books.book_id"], ondelete="CASCADE"),
    )
