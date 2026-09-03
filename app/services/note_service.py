from fastapi import Depends, HTTPException

from app.models.notes import Note
from app.repositories.book_repository import BookRepository
from app.repositories.note_repository import NoteRepository
from app.repositories.shelf_repository import ShelfRepository
from app.repositories.user_repository import UserRepository
from app.schemas.notes_schemas import NoteCreate, NoteUpdate
from app.schemas.params import NoteFilterParams


class NoteService:
    """
    Сервис для работы с заметками.
    """

    def __init__(
        self,
        note_repository: NoteRepository = Depends(),
        user_repository: UserRepository = Depends(),
        book_repository: BookRepository = Depends(),
        shelf_repository: ShelfRepository = Depends(),
    ) -> None:
        """
        Инициализация сервиса.
        Args:
            note_repository: NoteRepository -- репозиторий заметок.
            user_repository: UserRepository -- репозиторий пользователей.
            book_repository: BookRepository -- репозиторий книг.
            shelf_repository: ShelfRepository -- репозиторий полок пользователей.
        """
        self.note_repository = note_repository
        self.user_repository = user_repository
        self.book_repository = book_repository
        self.shelf_repository = shelf_repository

    async def get_by_id(self, user_id: int, book_id: int, note_id: int) -> Note:
        """
        Получение заметки по id.
        Args:
            user_id: int -- id пользователя.
            book_id: int -- id книги.
            note_id: int -- id заметки.

        Returns:
            Note -- заметка.
        """
        await self._check_book_on_shelf(user_id=user_id, book_id=book_id)

        note = await self.note_repository.get_by_id(id=note_id, user_id=user_id, book_id=book_id)
        if note is None:
            raise HTTPException(status_code=404, detail="Note not found.")
        return note

    async def get_by_shelf_entry(self, user_id: int, book_id: int, note_filter_params: NoteFilterParams) -> list[Note]:
        """
        Получение заметок по полке пользователя.
        Args:
            user_id: int -- id пользователя.
            book_id: int -- id книги.
            note_filter_params: NoteFilterParams -- параметры фильтрации заметок.

        Returns:
            list[Note] -- список заметок.
        """
        await self._check_book_on_shelf(user_id=user_id, book_id=book_id)
        return list(
            await self.note_repository.get_by_shelf_entry(
                user_id=user_id, book_id=book_id, note_filters=note_filter_params
            )
        )

    async def create(self, user_id: int, book_id: int, note_create: NoteCreate) -> Note:
        """
        Создание заметки.
        Args:
            user_id: int -- id пользователя.
            book_id: int -- id книги.
            note_create: NoteCreate -- данные для создания заметки.

        Returns:
            Note -- созданная заметка.
        """
        await self._check_book_on_shelf(user_id=user_id, book_id=book_id)
        data = {"user_id": user_id, "book_id": book_id, **note_create.model_dump()}
        return await self.note_repository.create(data)

    async def update(self, user_id: int, book_id: int, note_id: int, note_update: NoteUpdate) -> Note:
        """
        Частичное обновление заметки (PATCH).
        Args:
            user_id: int -- id пользователя.
            book_id: int -- id книги.
            note_id: int -- id заметки.
            note_update: NoteUpdate -- данные для обновления заметки.

        Returns:
            Note -- обновленная заметка.
        """
        await self._check_book_on_shelf(user_id=user_id, book_id=book_id)

        note = await self.note_repository.get_by_id(id=note_id, user_id=user_id, book_id=book_id)
        if note is None:
            raise HTTPException(status_code=404, detail="Note not found.")

        return await self.note_repository.update(
            id=note_id, user_id=user_id, book_id=book_id, data=note_update.model_dump(exclude_unset=True)
        )

    async def replace(self, user_id: int, book_id: int, note_id: int, note_create: NoteCreate) -> Note:
        """
        Полное обновление заметки (PUT).
        Args:
            user_id: int -- id пользователя.
            book_id: int -- id книги.
            note_id: int -- id заметки.
            note_create: NoteCreate -- данные для обновления заметки.

        Returns:
            Note -- обновленная заметка.
        """
        await self._check_book_on_shelf(user_id=user_id, book_id=book_id)

        note = await self.note_repository.get_by_id(id=note_id, user_id=user_id, book_id=book_id)
        if note is None:
            raise HTTPException(status_code=404, detail="Note not found.")

        return await self.note_repository.update(
            id=note_id, user_id=user_id, book_id=book_id, data=note_create.model_dump()
        )

    async def delete(self, user_id: int, book_id: int, note_id: int) -> None:
        """
        Удаление заметки.
        Args:
            user_id: int -- id пользователя.
            book_id: int -- id книги.
            note_id: int -- id заметки.

        Returns:
            None -- заметка удалена.
        """
        await self._check_book_on_shelf(user_id=user_id, book_id=book_id)
        note = await self.note_repository.get_by_id(id=note_id, user_id=user_id, book_id=book_id)
        if note is None:
            raise HTTPException(status_code=404, detail="Note not found.")
        await self.note_repository.delete(id=note_id, user_id=user_id, book_id=book_id)

    async def _check_book_on_shelf(self, user_id: int, book_id: int) -> None:
        """
        Проверка существования пользователя, книги и книги на полке пользователя.
        Args:
            user_id: int -- id пользователя.
            book_id: int -- id книги.

        Returns:
            bool -- True, если полка пользователя существует.
        """
        book = await self.book_repository.get_by_id(id=book_id)
        if book is None:
            raise HTTPException(status_code=404, detail="Book not found.")

        if not await self.shelf_repository.exists_by_user_id_and_book_id(user_id=user_id, book_id=book_id):
            raise HTTPException(status_code=404, detail="Shelf entry not found.")
