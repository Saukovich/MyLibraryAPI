import pytest
from fastapi import HTTPException

from app.repositories.author_repository import AuthorRepository
from app.repositories.book_repository import BookRepository
from app.schemas.author_schemas import ExistingAuthorRef, NewAuthorRef
from app.schemas.book_schemas import BookCreate, BookUpdate
from app.services.book_service import BookService


@pytest.fixture
def book_service(db_session):
    """Фикстура для создания экземпляра BookService."""
    book_repository = BookRepository(db_session)
    author_repository = AuthorRepository(db_session)
    return BookService(book_repository, author_repository)


@pytest.mark.asyncio
async def test_book_service_get_authors_happy_path(book_service):
    """Тест получения авторов. Получает существующих авторов."""
    author = await book_service.author_repository.create({"fullname": "Test Author", "birth_year": 1990})

    authors = await book_service._get_authors(
        [ExistingAuthorRef(id=author.id), NewAuthorRef(fullname="Another Author", birth_year=1980)]
    )

    assert len(authors) == 2 and authors[0].id == author.id and authors[1].fullname == "Another Author"


@pytest.mark.asyncio
async def test_book_service_get_authors_not_found_raises_404(book_service):
    """Тест получения авторов, которых нет в базе данных. Вызывает исключение с кодом 404."""
    with pytest.raises(HTTPException) as exc_info:
        await book_service._get_authors([ExistingAuthorRef(id=99999)])
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_book_service_get_by_id_happy_path(book_service):
    """Тест получения книги по ID. Получает существующую книгу."""
    book = await book_service.book_repository.create({"title": "Test Book", "release_year": 2024})

    got_book = await book_service.get_by_id(book.id)
    assert got_book.id == book.id and got_book.title == book.title and got_book.release_year == book.release_year


@pytest.mark.asyncio
async def test_book_service_get_by_id_not_found_raises_404(book_service):
    """Тест получения несуществующей книги. Вызывает исключение с кодом 404."""
    with pytest.raises(HTTPException) as exc_info:
        await book_service.get_by_id(99999)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_book_service_create_happy_path(book_service):
    """Тест создания книги с авторами. Создает новую книгу с авторами."""
    book_create = BookCreate(
        title="Test Book", release_year=2024, authors=[NewAuthorRef(fullname="Test Author", birth_year=1990)]
    )

    book = await book_service.create(book_create)
    assert (
        book.title == book_create.title
        and book.release_year == book_create.release_year
        and len(book.authors) == 1
        and book.authors[0].fullname == "Test Author"
    )


@pytest.mark.asyncio
async def test_book_service_update_without_authors_happy_path(book_service):
    """Тест обновления книги без авторов. Обновляет существующую книгу."""
    book = await book_service.book_repository.create({"title": "Test Book", "release_year": 2024})

    book_update = BookUpdate(title="Updated Book", release_year=2025)
    updated_book = await book_service.update(book.id, book_update)

    assert (
        updated_book.title == book_update.title
        and updated_book.release_year == book_update.release_year
        and len(updated_book.authors) == 0
    )


@pytest.mark.asyncio
async def test_book_service_update_with_authors_raises_404(book_service):
    """Тест обновления книги с авторами, которых нет в базе данных. Вызывает исключение с кодом 404."""
    book = await book_service.book_repository.create({"title": "Test Book", "release_year": 2024})

    book_update = BookUpdate(
        title="Updated Book", release_year=2025, authors=[NewAuthorRef(fullname="Test Author", birth_year=1990)]
    )
    updated_book = await book_service.update(book.id, book_update)

    assert (
        updated_book.title == book_update.title
        and updated_book.release_year == book_update.release_year
        and len(updated_book.authors) == 1
        and updated_book.authors[0].fullname == "Test Author"
    )


@pytest.mark.asyncio
async def test_book_service_update_not_found_raises_404(book_service):
    """Тест обновления несуществующей книги. Вызывает исключение с кодом 404."""
    with pytest.raises(HTTPException) as exc_info:
        await book_service.update(99999, BookUpdate(title="Updated Book", release_year=2025))
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_book_service_replace_happy_path(book_service):
    """Тест замены книги. Заменяет существующую книгу."""
    book = await book_service.book_repository.create({"title": "Test Book", "release_year": 2024})

    book_replace = BookCreate(
        title="Updated Book", release_year=2025, authors=[NewAuthorRef(fullname="Test Author", birth_year=1990)]
    )
    replaced_book = await book_service.replace(book.id, book_replace)

    assert (
        replaced_book.title == book_replace.title
        and replaced_book.release_year == book_replace.release_year
        and len(replaced_book.authors) == 1
        and replaced_book.authors[0].fullname == "Test Author"
    )


@pytest.mark.asyncio
async def test_book_service_replace_not_found_raises_404(book_service):
    """Тест замены несуществующей книги. Вызывает исключение с кодом 404."""
    with pytest.raises(HTTPException) as exc_info:
        await book_service.replace(99999, BookCreate(title="Updated Book", release_year=2025, authors=[]))
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_book_service_delete_happy_path(book_service):
    """Тест удаления книги. Удаляет существующую книгу."""
    book = await book_service.book_repository.create({"title": "Test Book", "release_year": 2024})

    await book_service.delete(book.id)

    # Проверяем, что книга больше не существует
    with pytest.raises(HTTPException) as exc_info:
        await book_service.get_by_id(book.id)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_book_service_delete_not_found_raises_404(book_service):
    """Тест удаления несуществующей книги. Вызывает исключение с кодом 404."""
    with pytest.raises(HTTPException) as exc_info:
        await book_service.delete(99999)
    assert exc_info.value.status_code == 404
