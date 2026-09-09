from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import BookStatus


class ShelfEntryBase(BaseModel):
    """Базовая схема для записи на полке."""

    model_config = ConfigDict(from_attributes=True)

    status: BookStatus = BookStatus.PLANNED
    rating: int | None = Field(None, ge=1, le=10)

    @model_validator(mode="after")
    def check_rating(self):
        """Проверяем, что рейтинг указывается только для прочитанной книги."""
        if self.rating is not None and self.status != BookStatus.READ:
            raise ValueError("Рейтинг можно указывать только для прочитанных книг")
        return self


class ShelfEntryResponse(ShelfEntryBase):
    """Схема для ответа на запрос о записи на полке."""

    book_id: int
    title: str
    authors: list[str]
    release_year: int
    added_at: datetime

    @model_validator(mode="before")
    def flatten_shelf_entry(cls, data):
        if hasattr(data, "book"):  # UserBook ORM-объект
            return {
                "book_id": data.book.id,
                "title": data.book.title,
                "authors": [a.fullname for a in data.book.authors],
                "release_year": data.book.release_year,
                "status": data.status,
                "rating": data.rating,
                "added_at": data.added_at,
            }
        return data


class ShelfEntryCreate(ShelfEntryBase):
    """Схема для создания новой записи на полке."""

    pass


class ShelfEntryUpdate(BaseModel):
    """Схема для обновления статуса или рейтинга книги на полке."""

    status: BookStatus | None = None
    rating: int | None = Field(None, ge=1, le=10)

    @model_validator(mode="after")
    def check_rating(self):
        """Проверяем, что рейтинг указывается только для прочитанной книг."""
        if self.rating is not None and self.status is not None and self.status != BookStatus.READ:
            raise ValueError("Рейтинг можно указывать только для прочитанных книг")
        return self


class ShelfStatsResponse(BaseModel):
    """Схема для статистики по полке."""

    number_of_books: int
    avg_rating: float | None
    favorite_author: str | None
