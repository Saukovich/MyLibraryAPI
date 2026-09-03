import pytest
from fastapi import HTTPException

from app.models.enums import BookStatus
from app.repositories.book_repository import BookRepository
from app.repositories.shelf_repository import ShelfRepository
from app.repositories.user_repository import UserRepository
from app.schemas.shelf_schemas import ShelfEntryCreate, ShelfEntryUpdate
from app.services.shelf_service import ShelfService


@pytest.fixture
def shelf_service(db_session):
    """Фикстура для сервиса полки."""
    book_repository = BookRepository(db_session)
    shelf_repository = ShelfRepository(db_session)
    return ShelfService(shelf_repository, book_repository)


@pytest.fixture
def user_repository(db_session):
    """Фикстура для репозитория пользователей."""
    return UserRepository(db_session)


@pytest.mark.asyncio
async def test_shelf_service_check_book_happy_path(shelf_service):
    """Тест с корректным book_id."""
    book = await shelf_service.book_repository.create({"title": "Test Book", "release_year": 2023})
    result = await shelf_service._check_book(book.id)
    assert result is None


@pytest.mark.asyncio
async def test_shelf_service_check_book_not_found_raises_404(shelf_service):
    """Тест с несуществующим book_id. Вызывает исключение с кодом 404."""
    with pytest.raises(HTTPException) as exc_info:
        await shelf_service._check_book(book_id=99999)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status,rating",
    [
        (BookStatus.PLANNED, None),
        (BookStatus.READING, None),
        (BookStatus.READ, 10),
        (BookStatus.ABANDONED, None),
    ],
)
async def test_shelf_service_check_data_happy_path(shelf_service, user_repository, status, rating):
    """Тест с корректными данными."""
    user = await user_repository.create(
        {"username": "test_user", "email": "test@example.com", "password_hash": "test_password_hash"}
    )
    book = await shelf_service.book_repository.create({"title": "Test Book", "release_year": 2023})

    shelf_entry = await shelf_service.shelf_repository.create({"user_id": user.id, "book_id": book.id})

    new_data = {"status": status, "rating": rating}
    result = await shelf_service._check_data(shelf_entry, new_data)

    assert result is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status,rating",
    [
        (BookStatus.READING, 10),
        (BookStatus.PLANNED, 10),
        (BookStatus.ABANDONED, 10),
    ],
)
async def test_shelf_service_check_data_invalid_data_raises_400(shelf_service, user_repository, status, rating):
    """Тест с некорректными данными. Вызывает исключение с кодом 400."""
    user = await user_repository.create(
        {"username": "test_user", "email": "test@example.com", "password_hash": "test_password_hash"}
    )
    book = await shelf_service.book_repository.create({"title": "Test Book", "release_year": 2023})

    shelf_entry = await shelf_service.shelf_repository.create({"user_id": user.id, "book_id": book.id})

    new_data = {"status": status, "rating": rating}
    with pytest.raises(HTTPException) as exc_info:
        await shelf_service._check_data(shelf_entry, new_data)
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_shelf_service_get_by_id_happy_path(shelf_service, user_repository):
    """Тест получения записи на полке."""
    user = await user_repository.create(
        {"username": "test_user", "email": "test@example.com", "password_hash": "test_password_hash"}
    )
    book = await shelf_service.book_repository.create({"title": "Test Book", "release_year": 2023})

    shelf_entry = await shelf_service.shelf_repository.create({"user_id": user.id, "book_id": book.id})

    got_entry = await shelf_service.get_by_id(user.id, book.id)
    assert got_entry.user_id == shelf_entry.user_id and got_entry.book_id == shelf_entry.book_id


@pytest.mark.asyncio
async def test_shelf_service_get_by_id_not_found_raises_404(shelf_service):
    """Тест получения несуществующей записи на полке. Вызывает исключение с кодом 404."""
    book = await shelf_service.book_repository.create({"title": "Test Book", "release_year": 2023})

    with pytest.raises(HTTPException) as exc_info:
        await shelf_service.get_by_id(user_id=99999, book_id=book.id)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_shelf_service_create_happy_path(shelf_service, user_repository):
    """Тест создания записи на полке."""
    user = await user_repository.create(
        {"username": "test_user", "email": "test@example.com", "password_hash": "test_password_hash"}
    )
    book = await shelf_service.book_repository.create({"title": "Test Book", "release_year": 2023})

    shelf_entry_create = ShelfEntryCreate(status=BookStatus.PLANNED, rating=None)
    shelf_entry = await shelf_service.create(user_id=user.id, book_id=book.id, shelf_entry_create=shelf_entry_create)

    assert (
        shelf_entry.user_id == user.id
        and shelf_entry.book_id == book.id
        and shelf_entry.status == BookStatus.PLANNED
        and shelf_entry.rating is None
    )


@pytest.mark.asyncio
async def test_shelf_service_create_shelf_entry_already_exists_raises_409(shelf_service, user_repository):
    """Тест создания записи на полке, когда запись уже существует. Вызывает исключение с кодом 409."""
    user = await user_repository.create(
        {"username": "test_user", "email": "test@example.com", "password_hash": "test_password_hash"}
    )
    book = await shelf_service.book_repository.create({"title": "Test Book", "release_year": 2023})

    shelf_entry_create = ShelfEntryCreate(status=BookStatus.PLANNED, rating=None)
    await shelf_service.create(user_id=user.id, book_id=book.id, shelf_entry_create=shelf_entry_create)

    with pytest.raises(HTTPException) as exc_info:
        await shelf_service.create(user_id=user.id, book_id=book.id, shelf_entry_create=shelf_entry_create)
    assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_shelf_service_update_happy_path(shelf_service, user_repository):
    """Тест частичного обновления записи на полке."""
    user = await user_repository.create(
        {"username": "test_user", "email": "test@example.com", "password_hash": "test_password_hash"}
    )
    book = await shelf_service.book_repository.create({"title": "Test Book", "release_year": 2023})

    await shelf_service.shelf_repository.create({"user_id": user.id, "book_id": book.id})

    shelf_entry_update = ShelfEntryUpdate(status=BookStatus.READ, rating=10)
    shelf_entry = await shelf_service.update(user.id, book.id, shelf_entry_update)

    assert (
        shelf_entry.status == BookStatus.READ
        and shelf_entry.rating == 10
        and shelf_entry.user_id == user.id
        and shelf_entry.book_id == book.id
    )


@pytest.mark.asyncio
async def test_shelf_service_update_not_found_raises_404(shelf_service):
    """Тест частичного обновления несуществующей записи на полке. Вызывает исключение с кодом 404."""
    book = await shelf_service.book_repository.create({"title": "Test Book", "release_year": 2023})

    with pytest.raises(HTTPException) as exc_info:
        await shelf_service.update(
            user_id=99999, book_id=book.id, shelf_entry_update=ShelfEntryUpdate(status=BookStatus.READ, rating=10)
        )
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_shelf_service_replace_happy_path(shelf_service, user_repository):
    """Тест полного обновления записи на полке."""
    user = await user_repository.create(
        {"username": "test_user", "email": "test@example.com", "password_hash": "test_password_hash"}
    )
    book = await shelf_service.book_repository.create({"title": "Test Book", "release_year": 2023})

    await shelf_service.shelf_repository.create({"user_id": user.id, "book_id": book.id})

    shelf_entry_replace = ShelfEntryCreate(status=BookStatus.READ, rating=10)
    shelf_entry = await shelf_service.replace(user.id, book.id, shelf_entry_replace)

    assert (
        shelf_entry.status == BookStatus.READ
        and shelf_entry.rating == 10
        and shelf_entry.user_id == user.id
        and shelf_entry.book_id == book.id
    )


@pytest.mark.asyncio
async def test_shelf_service_replace_not_found_raises_404(shelf_service):
    """Тест полного обновления несуществующей записи на полке. Вызывает исключение с кодом 404."""
    book = await shelf_service.book_repository.create({"title": "Test Book", "release_year": 2023})

    with pytest.raises(HTTPException) as exc_info:
        await shelf_service.replace(
            user_id=99999, book_id=book.id, shelf_entry_create=ShelfEntryCreate(status=BookStatus.READ, rating=10)
        )
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_shelf_service_delete_happy_path(shelf_service, user_repository):
    """Тест удаления записи на полке."""
    user = await user_repository.create(
        {"username": "test_user", "email": "test@example.com", "password_hash": "test_password_hash"}
    )
    book = await shelf_service.book_repository.create({"title": "Test Book", "release_year": 2023})

    await shelf_service.shelf_repository.create({"user_id": user.id, "book_id": book.id})

    await shelf_service.delete(user.id, book.id)

    # Проверяем, что запись удалена
    with pytest.raises(HTTPException) as exc_info:
        await shelf_service.get_by_id(user.id, book.id)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_shelf_service_delete_not_found_raises_404(shelf_service):
    """Тест удаления несуществующей записи на полке. Вызывает исключение с кодом 404."""
    book = await shelf_service.book_repository.create({"title": "Test Book", "release_year": 2023})

    with pytest.raises(HTTPException) as exc_info:
        await shelf_service.delete(user_id=99999, book_id=book.id)
    assert exc_info.value.status_code == 404
