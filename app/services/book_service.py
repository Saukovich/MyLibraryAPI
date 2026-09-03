from typing import Sequence

from fastapi import Depends, HTTPException

from app.models.authors import Author
from app.models.books import Book
from app.repositories.author_repository import AuthorRepository
from app.repositories.book_repository import BookRepository
from app.repositories.dto import PopularBookRow
from app.schemas.author_schemas import AuthorRef, ExistingAuthorRef, NewAuthorRef
from app.schemas.book_schemas import BookCreate, BookUpdate
from app.schemas.params import BookFilterParams


class BookService:
    """
    Класс сервиса для работы с книгами.
    """

    def __init__(
        self, book_repository: BookRepository = Depends(), author_repository: AuthorRepository = Depends()
    ) -> None:
        """
        Инициализация сервиса.
        Args:
            book_repository: BookRepository -- репозиторий книг.
            author_repository: AuthorRepository -- репозиторий авторов.
        """
        self.book_repository = book_repository
        self.author_repository = author_repository

    async def get_by_id(self, book_id: int) -> Book:
        """
        Получение книги по id.
        Args:
            book_id: int -- id книги.

        Returns:
            Book -- книга.
        """
        book = await self.book_repository.get_by_id(id=book_id)
        if book is None:  # Если книга не найдена
            raise HTTPException(status_code=404, detail="Book not found.")
        return book

    async def get_by_filters(self, book_filter_params: BookFilterParams) -> list[Book]:
        """
        Получение книг по фильтрам.
        Args:
            book_filter_params: BookFilterParams -- параметры фильтрации.

        Returns:
            list[Book] -- список книг.
        """
        return list(await self.book_repository.get_by_filters(book_filter_params))

    async def get_popular(self, limit: int = 10) -> list[PopularBookRow]:
        """
        Получение популярных книг.
        Args:
            limit: int -- количество возвращаемых книг.

        Returns:
             list[PopularBookRow] -- список популярных книг.
        """
        return list(await self.book_repository.get_popular(limit))

    async def create(self, data: BookCreate) -> Book:
        """
        Создание книги.
        Args:
            data: BookCreate -- данные для создания книги.

        Returns:
            Book -- созданная книга.
        """
        authors = await self._get_authors(data.authors)  # Получаем список авторов
        book = await self.book_repository.create(data.model_dump(exclude={"authors"}))  # Создаем книгу
        await self.book_repository.set_authors(book=book, authors=authors)  # Устанавливаем авторов
        return book

    async def update(self, book_id: int, data: BookUpdate) -> Book:
        """
        Частичное обновление книги (PATCH).
        Args:
            book_id: int -- id обновляемой книги.
            data: BookUpdate -- данные для обновления книги.

        Returns:
            Book -- обновленная книга.
        """
        book = await self.book_repository.get_by_id(id=book_id)
        if book is None:
            raise HTTPException(status_code=404, detail="Book not found.")

        book = await self.book_repository.update(
            data=data.model_dump(exclude={"authors"}, exclude_unset=True), id=book_id
        )  # Обновляем книгу
        if data.authors is not None:
            authors = await self._get_authors(data.authors)  # Получаем список авторов
            await self.book_repository.set_authors(book=book, authors=authors)  # Устанавливаем авторов
        return book

    async def replace(self, book_id: int, data: BookCreate) -> Book:
        """
        Полное обновление книги (PUT).
        Args:
            book_id: int -- id обновляемой книги.
            data: BookCreate -- данные для обновления книги.

        Returns:
            Book -- обновленная книга.
        """
        book = await self.book_repository.get_by_id(id=book_id)
        if book is None:
            raise HTTPException(status_code=404, detail="Book not found.")

        authors = await self._get_authors(data.authors)  # Получаем список авторов
        book = await self.book_repository.update(
            data=data.model_dump(exclude={"authors"}), id=book_id
        )  # Обновляем книгу
        await self.book_repository.set_authors(book=book, authors=authors)  # Устанавливаем авторов
        return book

    async def delete(self, book_id: int) -> None:
        """
        Удаление книги.
        Args:
            book_id: int -- id удаляемой книги.

        Returns:
            None -- книга удалена.
        """
        book = await self.book_repository.get_by_id(id=book_id)
        if book is None:
            raise HTTPException(status_code=404, detail="Book not found.")
        await self.book_repository.delete(id=book_id)

    async def exists_by_title(self, title: str) -> bool:
        """
        Проверка существования книги по названию.
        Args:
            title: str -- название книги.

        Returns:
            bool -- True, если книга существует, иначе False.
        """
        return await self.book_repository.exists_by_title(title)

    async def _get_authors(self, authors: list[AuthorRef]) -> Sequence[Author]:
        """
        Вспомогательный метод для получения авторов из AuthorRef.
        Args:
            authors: list[AuthorRef] -- список авторов (либо id существующего автора, либо данные для создания нового автора).

        Returns:
            Sequence[Author] -- список авторов.
        """
        result = []
        for a in authors:
            if isinstance(a, ExistingAuthorRef):  # Если автор уже существует
                author = await self.author_repository.get_by_id(id=a.id)
                if author is None:  # Если автор не найден
                    raise HTTPException(status_code=404, detail="Author not found.")
                result.append(author)
            elif isinstance(a, NewAuthorRef):  # Если автора нужно создать
                author = await self.author_repository.create(a.model_dump())
                result.append(author)
        return result
