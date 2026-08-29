from typing import Sequence

from sqlalchemy import select

from app.core.database import SessionDep
from app.models.authors import Author
from app.schemas.params import AuthorFilterParams

from .base_repository import BaseRepository


class AuthorRepository(BaseRepository[Author]):
    """Репозиторий для работы с авторами.

    get_by_filters: Получение авторов по фильтрам."""

    def __init__(self, session: SessionDep):
        """
        Инициализация репозитория.
        Args:
            session: SessionDep -- сессия базы данных.
        """
        super().__init__(Author, session)

    async def get_by_filters(self, author_filters: AuthorFilterParams) -> Sequence[Author]:
        """
        Получение авторов по фильтрам.
        Args:
            author_filters: AuthorFilterParams -- фильтры.

        Returns:
            Sequence[Author]: Список авторов.
        """

        filters = []
        if author_filters.fullname:  # фильтр по имени автора
            filters.append(Author.fullname.ilike(f"%{author_filters.fullname}%"))
        if author_filters.birth_year_min:  # фильтр по году рождения (не меньше)
            filters.append(Author.birth_year >= author_filters.birth_year_min)
        if author_filters.birth_year_max:  # фильтр по году рождения (не больше)
            filters.append(Author.birth_year <= author_filters.birth_year_max)
        if author_filters.is_dead is not None:  # фильтр по статусу жизни автора
            if author_filters.is_dead:
                filters.append(Author.death_year.isnot(None))
            else:
                filters.append(Author.death_year.is_(None))
        if author_filters.death_year_min:  # фильтр по году смерти (не меньше)
            filters.append(Author.death_year >= author_filters.death_year_min)
        if author_filters.death_year_max:  # фильтр по году смерти (не больше)
            filters.append(Author.death_year <= author_filters.death_year_max)

        sort_by = None
        if author_filters.sort_by:  # сортировка
            if author_filters.sort_by == "id":  # сортировка по id
                sort_by = Author.id
            elif author_filters.sort_by == "fullname":  # сортировка по имени автора
                sort_by = Author.fullname
            elif author_filters.sort_by == "birth_year":  # сортировка по году рождения
                sort_by = Author.birth_year
            elif author_filters.sort_by == "death_year":  # сортировка по году смерти
                sort_by = Author.death_year

            if author_filters.order_by == "asc":  # сортировка по возрастанию
                sort_by = sort_by.asc()
            if author_filters.order_by == "desc":  # сортировка по убыванию
                sort_by = sort_by.desc()

        query = (
            select(Author).where(*filters).order_by(sort_by).limit(author_filters.limit).offset(author_filters.offset)
        )

        result = await self.session.execute(query)
        return result.scalars().all()
