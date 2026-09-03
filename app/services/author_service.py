from fastapi import HTTPException

from app.models.authors import Author
from app.repositories.author_repository import AuthorRepository
from app.schemas.author_schemas import AuthorCreate, AuthorUpdate
from app.schemas.params import AuthorFilterParams


class AuthorService:
    """Сервис для работы с авторами."""

    def __init__(self, author_repository: AuthorRepository) -> None:
        """Инициализация сервиса."""
        self.author_repository = author_repository

    async def get_by_id(self, author_id: int) -> Author:
        """
        Получение автора по id.
        Args:
            author_id: int -- id автора.

        Returns:
            Author -- автор.
        """
        author = await self.author_repository.get_by_id(id=author_id)
        if author is None:  # проверка на существование автора
            raise HTTPException(status_code=404, detail="Author not found.")
        return author

    async def get_by_filters(self, author_filter_params: AuthorFilterParams) -> list[Author]:
        """
        Получение авторов по фильтрам.
        Args:
            author_filter_params: AuthorFilterParams -- параметры фильтрации.

        Returns:
            list[Author] -- список авторов.
        """
        return list(await self.author_repository.get_by_filters(author_filter_params))

    async def create(self, data: AuthorCreate) -> Author:
        """
        Создание автора.
        Args:
            data: AuthorCreate -- данные для создания автора.

        Returns:
            Author -- созданный автор.
        """
        return await self.author_repository.create(data.model_dump())

    async def update(self, author_id: int, data: AuthorUpdate) -> Author:
        """
        Частичное обновление автора (PATCH).
        Args:
            author_id: int -- id автора.
            data: AuthorCreate -- данные для обновления автора.

        Returns:
            Author -- обновленный автор.
        """
        author = await self.author_repository.get_by_id(id=author_id)
        if author is None:  # проверка на существование автора
            raise HTTPException(status_code=404, detail="Author not found.")
        return await self.author_repository.update(data.model_dump(exclude_unset=True), id=author_id)

    async def replace(self, author_id: int, data: AuthorCreate) -> Author:
        """
        Полное обновление автора (PUT).
        Args:
            author_id: int -- id автора.
            data: AuthorCreate -- данные для обновления автора.

        Returns:
            Author -- обновленный автор.
        """
        author = await self.author_repository.get_by_id(id=author_id)
        if author is None:  # проверка на существование автора
            raise HTTPException(status_code=404, detail="Author not found.")
        return await self.author_repository.update(data.model_dump(), id=author_id)

    async def delete(self, author_id: int) -> None:
        """
        Удаление автора.
        Args:
            author_id: int -- id автора.

        Returns:
            None -- автор удален.
        """
        author = await self.author_repository.get_by_id(id=author_id)
        if author is None:  # проверка на существование автора
            raise HTTPException(status_code=404, detail="Author not found.")
        await self.author_repository.delete(id=author_id)
