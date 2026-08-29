from typing import Sequence

from sqlalchemy import exists, func, select
from sqlalchemy.orm import selectinload

from app.core.database import SessionDep
from app.models.authors import Author
from app.models.book_authors import BookAuthor
from app.models.books import Book
from app.models.user_books import UserBook
from app.schemas.params import ShelfFilterParams

from .base_repository import BaseRepository
from .dto import ShelfStatsRow


class ShelfRepository(BaseRepository[UserBook]):
    """Репозиторий для работы с книгами на полке пользователя."""

    def __init__(self, db_session: SessionDep):
        """
        Инициализация репозитория.
        Args:
            db_session: SessionDep - сессия базы данных.
        """
        super().__init__(UserBook, db_session)

    async def get_by_id(self, **composite_id) -> UserBook | None:
        """
        Получение книги на полке пользователя по id.
        Args:
            **composite_id: dict -- словарь с id книги и id пользователя.
            В качестве ключей словаря должны быть поля модели UserBook, в качестве значений -- их значения.
                Пример: {book_id: 1, user_id: 2}

        Returns:
            UserBook | None -- книга на полке пользователя или None, если книга не найдена.
        """
        query = (
            select(self.model)
            .options(selectinload(self.model.book).selectinload(Book.authors))
            .filter_by(**composite_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_filters(self, user_id: int, shelf_filters: ShelfFilterParams) -> Sequence[UserBook]:
        """
        Получение книг на полке пользователя по фильтрам.
        Args:
            user_id: int -- id пользователя.
            shelf_filters: ShelfFilterParams -- фильтры для поиска книг на полке пользователя.

        Returns:
            Sequence[UserBook] -- список книг на полке пользователя.
        """
        filters = [self.model.user_id == user_id]
        need_author_join = False
        need_book_join = False

        if shelf_filters.author_id:  # фильтр по автору
            filters.append(BookAuthor.author_id == shelf_filters.author_id)
            need_author_join = True
        if shelf_filters.author_name:  # фильтр по автору по имени
            filters.append(Author.fullname.ilike(f"%{shelf_filters.author_name}%"))
            need_author_join = True
        if shelf_filters.title:  # фильтр по названию книги
            filters.append(Book.title.ilike(f"%{shelf_filters.title}%"))
            need_book_join = True
        if shelf_filters.one_author:  # фильтр по книгам с одним автором
            subquery = (
                select(BookAuthor.book_id).group_by(BookAuthor.book_id).having(func.count(BookAuthor.author_id) == 1)
            )
            filters.append(self.model.book_id.in_(subquery))
            need_book_join = True
            need_author_join = True
        if shelf_filters.release_year_min:  # фильтр по минимальному году выпуска
            filters.append(Book.release_year >= shelf_filters.release_year_min)
            need_book_join = True
        if shelf_filters.release_year_max:  # фильтр по максимальному году выпуска
            filters.append(Book.release_year <= shelf_filters.release_year_max)
            need_book_join = True
        if shelf_filters.status:  # фильтр по статусу
            filters.append(self.model.status == shelf_filters.status)
        if shelf_filters.min_rating:  # фильтр по минимальному рейтингу
            filters.append(self.model.rating >= shelf_filters.min_rating)
        if shelf_filters.added_at_min:  # фильтр по минимальной дате добавления
            filters.append(self.model.added_at >= shelf_filters.added_at_min)
        if shelf_filters.added_at_max:  # фильтр по максимальной дате добавления
            filters.append(self.model.added_at <= shelf_filters.added_at_max)

        sort_by = None
        if shelf_filters.sort_by:  # сортировка
            if shelf_filters.sort_by == "book_id":  # сортировка по book_id
                sort_by = Book.id
                need_book_join = True
            elif shelf_filters.sort_by == "title":  # сортировка по названию
                sort_by = Book.title
                need_book_join = True
            elif shelf_filters.sort_by == "release_year":  # сортировка по году выпуска
                sort_by = Book.release_year
                need_book_join = True
            elif shelf_filters.sort_by == "author_id":  # сортировка по автору по id автора
                sort_by = Author.id
                need_author_join = True  # Для сортировки по автору нужно сделать join
            elif shelf_filters.sort_by == "status":  # сортировка по статусу книги
                sort_by = self.model.status
            elif shelf_filters.sort_by == "rating":  # сортировка по рейтингу
                sort_by = self.model.rating
            elif shelf_filters.sort_by == "added_at":  # сортировка по дате добавления
                sort_by = self.model.added_at

            if shelf_filters.order_by == "asc":  # сортировка по возрастанию
                sort_by = sort_by.asc()
            elif shelf_filters.order_by == "desc":  # сортировка по убыванию
                sort_by = sort_by.desc()

        query = (
            select(self.model)
            .options(selectinload(self.model.book).selectinload(Book.authors))
            .where(*filters)
            .order_by(sort_by)
            .limit(shelf_filters.limit)
            .offset(shelf_filters.offset)
        )

        if need_book_join or need_author_join:
            query = query.join(Book, self.model.book_id == Book.id)
        if need_author_join:  # если есть фильтр по автору, то нужно сделать join
            query = query.join(BookAuthor, self.model.book_id == BookAuthor.book_id)
            if shelf_filters.author_name or shelf_filters.author_id or shelf_filters.sort_by == "author_id":
                query = query.join(Author, BookAuthor.author_id == Author.id)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_stats(self, user_id: int) -> ShelfStatsRow:
        """
        Получение статистики по полке пользователя.
        Args:
            user_id: int -- id пользователя.

        Returns:
            ShelfStatsRow -- статистика по полке пользователя.
        """
        # Получение количества книг и среднего рейтинга
        stats_query = select(func.count(self.model.book_id), func.avg(self.model.rating)).where(
            self.model.user_id == user_id
        )

        stats_result = await self.session.execute(stats_query)
        number_of_books, avg_rating = stats_result.one()

        # Получение наиболее популярного автора
        favorite_author_query = (
            select(Author.fullname)  # Выбираем имя автора
            .join(BookAuthor, Author.id == BookAuthor.author_id)  # Соединяем с таблицей BookAuthor,
            # чтобы получить список книг, написанных автором
            .join(self.model, BookAuthor.book_id == self.model.book_id)  # Соединяем с таблицей UserBook,
            # чтобы отфильтровать книги по пользователю и подсчитать количество книг для каждого автора
            .where(self.model.user_id == user_id)
            .group_by(Author.id)  # Группируем по id автора
            .order_by(func.count(self.model.book_id).desc())  # Сортируем по количеству книг (по убыванию)
            .limit(1)  # Берем только одного автора
        )
        favorite_author_result = await self.session.execute(favorite_author_query)
        favorite_author = favorite_author_result.scalar_one_or_none()

        return ShelfStatsRow(number_of_books=number_of_books, avg_rating=avg_rating, favorite_author=favorite_author)

    async def exists_by_user_id_and_book_id(self, user_id: int, book_id: int) -> bool:
        """
        Проверка, есть ли книга на полке пользователя.
        Args:
            user_id: int -- id пользователя.
            book_id: int -- id книги.

        Returns:
            bool -- True, если книга есть на полке пользователя, иначе False.
        """
        query = select(exists().where(self.model.user_id == user_id, self.model.book_id == book_id))
        result = await self.session.execute(query)
        return result.scalar_one()
