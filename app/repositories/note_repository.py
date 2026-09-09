from typing import Sequence

from sqlalchemy import select

from app.core.database import SessionDep
from app.models.notes import Note
from app.schemas.params import NoteFilterParams

from .base_repository import BaseRepository


class NoteRepository(BaseRepository[Note]):
    """Класс репозитория для работы с заметками."""

    def __init__(self, session: SessionDep):
        """
        Инициализация репозитория.
        Args:
            session: SessionDep -- сессия базы данных.
        """
        super().__init__(Note, session)

    async def get_by_shelf_entry(self, user_id: int, book_id: int, note_filters: NoteFilterParams) -> Sequence[Note]:
        """
        Получение заметок по id книги, id пользователя и фильтрам.
        Args:
            user_id: int -- id пользователя.
            book_id: int -- id книги.
            note_filters: NoteFilterParams -- фильтры.

        Returns:
            Sequence[Note] -- заметки, удовлетворяющие фильтрации.
        """
        filters = [self.model.user_id == user_id, self.model.book_id == book_id]

        if note_filters.page_min:  # минимальная страница
            filters.append(self.model.page >= note_filters.page_min)
        if note_filters.page_max:
            filters.append(self.model.page <= note_filters.page_max)
        sort_by = None
        if note_filters.sort_by:  # сортировка
            if note_filters.sort_by == "id":  # сортировка по id
                sort_by = self.model.id
            elif note_filters.sort_by == "page":  # сортировка по странице
                sort_by = self.model.page
            elif note_filters.sort_by == "text":  # сортировка по тексту
                sort_by = self.model.text
            elif note_filters.sort_by == "created_at":  # сортировка по дате создания
                sort_by = self.model.created_at

            if note_filters.order_by == "asc":  # сортировка по возрастанию
                sort_by = sort_by.asc()
            elif note_filters.order_by == "desc":  # сортировка по убыванию
                sort_by = sort_by.desc()

        query = (
            select(self.model)
            .where(*filters)
            .order_by(sort_by)
            .limit(note_filters.limit)
            .offset(note_filters.offset)
            .distinct()
        )

        result = await self.session.execute(query)
        return result.scalars().all()
