from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.author_schemas import AuthorRef


class BookBase(BaseModel):
    """Базовая схема книги."""

    model_config = ConfigDict(from_attributes=True)

    title: str = Field(min_length=1, max_length=50)
    release_year: int = Field(ge=0)


class BookResponse(BookBase):
    """Схема ответа на запрос книги."""

    id: int
    authors: list[str]

    @field_validator("authors", mode="before")
    def validate_authors(cls, v: list) -> list[str]:
        return [author.fullname for author in v]


class BookCreate(BookBase):
    """Схема создания книги."""

    authors: list[AuthorRef]


class BookUpdate(BookBase):
    """Схема обновления книги."""

    title: str | None = Field(None, min_length=1, max_length=50)
    release_year: int | None = Field(None, ge=0)
    authors: list[AuthorRef] | None = None


class PopularBookResponse(BookResponse):
    """Схема ответа на запрос популярных книг."""

    number_of_additions: int
    avg_rating: float | None

    @model_validator(mode="before")
    def flatten_popular_book_row(cls, data):
        """Разворачиваем PopularBookRow в словарь."""
        if hasattr(data, "book"):  # data - не dict, а PopularBookRow
            return {
                "id": data.book.id,
                "title": data.book.title,
                "release_year": data.book.release_year,
                "authors": data.book.authors,
                "number_of_additions": data.number_of_additions,
                "avg_rating": data.avg_rating,
            }
        return data
