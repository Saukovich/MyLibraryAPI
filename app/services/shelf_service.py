from fastapi import Depends, HTTPException

from app.models.enums import BookStatus
from app.models.user_books import UserBook
from app.repositories.book_repository import BookRepository
from app.repositories.dto import ShelfStatsRow
from app.repositories.shelf_repository import ShelfRepository
from app.schemas.params import ShelfFilterParams
from app.schemas.shelf_schemas import ShelfEntryCreate, ShelfEntryUpdate


class ShelfService:
    """
    Сервис полки пользователя.
    """

    def __init__(self, shelf_repository: ShelfRepository = Depends(), book_repository: BookRepository = Depends()):
        """
        Инициализация сервиса полки.
        Args:
            shelf_repository: shelf_repository -- репозиторий полки.
        """
        self.shelf_repository = shelf_repository
        self.book_repository = book_repository

    async def get_by_id(self, user_id: int, book_id: int) -> UserBook:
        """
        Получение книги с полки по id.
        Args:
            user_id: int -- id пользователя.
            book_id: int -- id книги.

        Returns:
            UserBook -- книга с полки.
        """
        await self._check_book(book_id=book_id)

        shelf_entry = await self.shelf_repository.get_by_id(user_id=user_id, book_id=book_id)
        if shelf_entry is None:
            raise HTTPException(status_code=404, detail="Shelf entry not found.")
        return shelf_entry

    async def get_by_filters(self, user_id: int, shelf_filter_params: ShelfFilterParams) -> list[UserBook]:
        """
        Получение книг с полки пользователя по фильтрам.
        Args:
            user_id: int -- id пользователя.
            shelf_filter_params: ShelfFilterParams -- параметры фильтрации.

        Returns:
            list[UserBook] -- книги с полки.
        """
        return list(await self.shelf_repository.get_by_filters(user_id=user_id, shelf_filters=shelf_filter_params))

    async def get_stats(self, user_id: int) -> ShelfStatsRow:
        """
        Получение статистики по полке пользователя.
        Args:
            user_id: int -- id пользователя.

        Returns:
            SheffStatsRow -- статистика по полке.
        """
        shelf_stats = await self.shelf_repository.get_stats(user_id=user_id)
        return shelf_stats

    async def create(self, user_id: int, book_id: int, shelf_entry_create: ShelfEntryCreate) -> UserBook:
        """
        Создание книги на полке.
        Args:
            user_id: int -- id пользователя.
            book_id: int -- id книги.
            shelf_entry_create: ShelfEntryCreate -- данные книги.

        Returns:
            UserBook -- созданная книга.
        """
        await self._check_book(book_id=book_id)

        if await self.shelf_repository.exists_by_user_id_and_book_id(user_id=user_id, book_id=book_id):
            raise HTTPException(status_code=409, detail="Shelf entry already exists.")
        data = {"user_id": user_id, "book_id": book_id, **shelf_entry_create.model_dump()}
        return await self.shelf_repository.create(data)

    async def update(self, user_id: int, book_id: int, shelf_entry_update: ShelfEntryUpdate) -> UserBook:
        """
        Частичное обновление книги на полке.
        Args:
            user_id: int -- id пользователя.
            book_id: int -- id книги.
            shelf_entry_update: ShelfEntryUpdate -- данные книги.

        Returns:
            UserBook -- обновленная книга.
        """
        await self._check_book(book_id=book_id)

        shelf_entry = await self.shelf_repository.get_by_id(user_id=user_id, book_id=book_id)
        if shelf_entry is None:
            raise HTTPException(status_code=404, detail="Shelf entry not found.")

        await self._check_data(shelf_entry=shelf_entry, new_data=shelf_entry_update.model_dump())

        return await self.shelf_repository.update(
            user_id=user_id, book_id=book_id, data=shelf_entry_update.model_dump(exclude_unset=True)
        )

    async def replace(self, user_id: int, book_id: int, shelf_entry_create: ShelfEntryCreate) -> UserBook:
        """
        Полночное обновление книги на полке (PUT).
        Args:
            user_id: int -- id пользователя.
            book_id: int -- id книги.
            shelf_entry_create: ShelfEntryCreate -- данные книги.

        Returns:
            UserBook -- обновленная книга.
        """
        await self._check_book(book_id=book_id)

        shelf_entry = await self.shelf_repository.get_by_id(user_id=user_id, book_id=book_id)
        if shelf_entry is None:
            raise HTTPException(status_code=404, detail="Shelf entry not found.")

        await self._check_data(shelf_entry=shelf_entry, new_data=shelf_entry_create.model_dump())

        return await self.shelf_repository.update(
            user_id=user_id, book_id=book_id, data=shelf_entry_create.model_dump()
        )

    async def delete(self, user_id: int, book_id: int) -> None:
        """
        Удаление книги с полки.
        Args:
            user_id: int -- id пользователя.
            book_id: int -- id книги.

        Returns:
            None -- книга удалена.
        """
        await self._check_book(book_id=book_id)

        shelf_entry = await self.shelf_repository.get_by_id(user_id=user_id, book_id=book_id)
        if shelf_entry is None:
            raise HTTPException(status_code=404, detail="Shelf entry not found.")

        await self.shelf_repository.delete(user_id=user_id, book_id=book_id)

    @staticmethod
    async def _check_data(shelf_entry: UserBook, new_data: dict) -> None:
        """
        Проверка новых данных на корректность.
        Args:
            shelf_entry: UserBook -- книга на полке.
            new_data: dict -- новые данные.

        Returns:
            None -- если данные корректны.
        """
        final_status = new_data.get("status", shelf_entry.status)  # Если статус не указан, берем старый статус
        final_rating = new_data.get("rating", shelf_entry.rating)  # Если рейтинг не указан, берем старый рейтинг

        if final_rating is not None and final_status != BookStatus.READ:
            raise HTTPException(status_code=400, detail="Rating can only be set for read books.")

        return None

    async def _check_book(self, book_id: int) -> None:
        """
        Проверка книги на существование.
        Args:
            book_id: int -- id книги.

        Returns:
            None -- если книга существует.
        """
        book = await self.book_repository.get_by_id(id=book_id)
        if book is None:
            raise HTTPException(status_code=404, detail="Book not found.")
