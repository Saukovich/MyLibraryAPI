from dataclasses import dataclass

from app.models import Book


@dataclass
class PopularBookRow:
    """
    DTO-класс для строки таблицы популярных книг.
    """

    book: Book
    number_of_additions: int
    avg_rating: float


@dataclass
class ShelfStatsRow:
    """
    DTO-класс для строки таблицы статистики полки.
    """

    number_of_books: int
    avg_rating: float
    favorite_author: str
