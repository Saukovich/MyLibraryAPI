from typing import Sequence

from sqlalchemy import exists, func, select
from sqlalchemy.orm import selectinload

from app.core.database import SessionDep
from app.models.authors import Author
from app.models.book_authors import BookAuthor
from app.models.books import Book
from app.models.user_books import UserBook
from app.repositories.dto import PopularBookRow
from app.schemas.params import BookFilterParams

from .base_repository import BaseRepository


class BookRepository(BaseRepository[Book]):
    """Репозиторий для работы с книгами."""

    def __init__(self, session: SessionDep):
        """Инициализация репозитория.
        Args:
            session: SessionDep -- сессия базы данных."""
        super().__init__(Book, session)

    async def get_by_id(self, **composite_id) -> Book | None:
        """
        Получение книги по id.
        Args:
            **composite_id: id книги.

        Returns:
            Book | None -- книга.
        """
        query = select(self.model).options(selectinload(self.model.authors)).filter_by(**composite_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_filters(self, book_filters: BookFilterParams) -> Sequence[Book]:
        """
        Получение книг по фильтрам.
        Args:
            book_filters: BookFilterParams -- фильтры.

        Returns:
            Sequence[Book] -- список книг.
        """
        filters = []
        need_author_join = False
        if book_filters.author_id:  # фильтр по автору
            filters.append(BookAuthor.author_id == book_filters.author_id)
            need_author_join = True
        if book_filters.author_name:  # фильтр по автору по имени
            filters.append(Author.fullname.ilike(f"%{book_filters.author_name}%"))
            need_author_join = True
        if book_filters.title:  # фильтр по названию книги
            filters.append(self.model.title.ilike(f"%{book_filters.title}%"))
        if book_filters.one_author:  # фильтр по книгам с одним автором
            subquery = (
                select(BookAuthor.book_id).group_by(BookAuthor.book_id).having(func.count(BookAuthor.author_id) == 1)
            )
            filters.append(self.model.id.in_(subquery))
        if book_filters.release_year_min:  # фильтр по минимальному году выпуска
            filters.append(self.model.release_year >= book_filters.release_year_min)
        if book_filters.release_year_max:  # фильтр по максимальному году выпуска
            filters.append(self.model.release_year <= book_filters.release_year_max)

        sort_by = None
        if book_filters.sort_by:  # сортировка
            if book_filters.sort_by == "id":  # сортировка по id
                sort_by = self.model.id
            elif book_filters.sort_by == "title":  # сортировка по названию
                sort_by = self.model.title
            elif book_filters.sort_by == "release_year":  # сортировка по году выпуска
                sort_by = self.model.release_year
            elif book_filters.sort_by == "author_id":  # сортировка по id автора
                sort_by = Author.id
                need_author_join = True  # для сортировки по автору нужно сделать join

            if book_filters.order_by == "asc":  # сортировка по возрастанию
                sort_by = sort_by.asc()
            elif book_filters.order_by == "desc":  # сортировка по убыванию
                sort_by = sort_by.desc()

        query = (
            select(self.model)
            .options(selectinload(self.model.authors))
            .where(*filters)
            .order_by(sort_by)
            .limit(book_filters.limit)
            .offset(book_filters.offset)
            .distinct()
        )

        if need_author_join:  # если есть фильтр по автору, то нужно сделать join
            query = query.join(BookAuthor, self.model.id == BookAuthor.book_id)
            if book_filters.author_name:
                query = query.join(Author, BookAuthor.author_id == Author.id)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def exists_by_title(self, title: str) -> bool:
        """
        Проверка существования книги по названию.
        Args:
            title: str -- название книги.

        Returns:
            bool -- True, если книга существует, иначе False.

        """
        query = select(exists().where(self.model.title.ilike(title)))
        result = await self.session.execute(query)
        return result.scalar()

    async def get_popular(self, limit: int = 10) -> Sequence[PopularBookRow]:
        """
        Получение популярных книг.
        Args:
            limit: int -- Количество возвращаемых книг.

        Returns:
            Sequence[PopularBookRow] -- список популярных книг.
        """
        query = (
            select(
                self.model,
                func.count(UserBook.book_id).label("number_of_additions"),
                func.avg(UserBook.rating).label("avg_rating"),
            )
            .join(UserBook, self.model.id == UserBook.book_id)
            .options(selectinload(self.model.authors))
            .group_by(self.model.id)
            .order_by(func.count(UserBook.book_id).desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return [PopularBookRow(book=row[0], number_of_additions=row[1], avg_rating=row[2]) for row in result.all()]

    async def set_authors(self, book: Book, authors: Sequence[Author]) -> None:
        """
        Полностью заменяет список авторов у книги.
        Args:
            book: Book -- книга (уже загруженный ORM-объект).
            authors: Sequence[Author] -- новый список авторов.
        """
        book.authors = list(authors)
        await self.session.flush()
