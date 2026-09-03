import pytest
from fastapi import HTTPException

from app.repositories.book_repository import BookRepository
from app.repositories.note_repository import NoteRepository
from app.repositories.shelf_repository import ShelfRepository
from app.repositories.user_repository import UserRepository
from app.schemas.notes_schemas import NoteCreate, NoteUpdate
from app.services.note_service import NoteService


@pytest.fixture
def note_service(db_session):
    """Фикстура для создания экземпляра NoteService."""
    note_repository = NoteRepository(db_session)
    user_repository = UserRepository(db_session)
    book_repository = BookRepository(db_session)
    shelf_repository = ShelfRepository(db_session)
    return NoteService(note_repository, user_repository, book_repository, shelf_repository)


@pytest.mark.asyncio
async def test_note_service_check_book_on_shelf_happy_path(note_service):
    user = await note_service.user_repository.create(
        {"username": "test_user", "email": "test_email@example.com", "password_hash": "test_password"}
    )

    book = await note_service.book_repository.create({"title": "Test Book", "release_year": 2023})

    await note_service.shelf_repository.create({"user_id": user.id, "book_id": book.id})

    result = await note_service._check_book_on_shelf(user.id, book.id)
    assert result is None


@pytest.mark.asyncio
async def test_note_service_check_book_on_shelf_book_not_found_raises_404(note_service):
    """Тест проверки наличия книги на полке. Вызывает исключение 404."""
    with pytest.raises(HTTPException) as exc_info:
        await note_service._check_book_on_shelf(99999, 99999)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_note_service_check_book_on_shelf_shelf_entry_not_found_raises_404(note_service):
    """Тест проверки наличия книги на полке. Вызывает исключение 404."""
    book = await note_service.book_repository.create({"title": "Test Book", "release_year": 2023})

    with pytest.raises(HTTPException) as exc_info:
        await note_service._check_book_on_shelf(99999, book.id)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_note_service_get_by_id_happy_path(note_service):
    """Тест получения заметки. Получает заметку и проверяет, что она действительно существует."""
    user = await note_service.user_repository.create(
        {"username": "test_user", "email": "test_email@example.com", "password_hash": "test_password"}
    )

    book = await note_service.book_repository.create({"title": "Test Book", "release_year": 2023})

    await note_service.shelf_repository.create({"user_id": user.id, "book_id": book.id})

    note = await note_service.note_repository.create(
        {"user_id": user.id, "book_id": book.id, "text": "Test note", "page": 10}
    )

    got_note = await note_service.get_by_id(user.id, book.id, note.id)
    assert (
        got_note.id == note.id
        and got_note.text == note.text
        and got_note.page == note.page
        and got_note.book_id == note.book_id
        and got_note.user_id == note.user_id
    )


@pytest.mark.asyncio
async def test_note_service_get_by_id_not_found_raises_404(note_service):
    """Тест получения заметки, которой не существует. Вызывает исключение 404."""
    user = await note_service.user_repository.create(
        {"username": "test_user", "email": "test_email@example.com", "password_hash": "test_password"}
    )

    book = await note_service.book_repository.create({"title": "Test Book", "release_year": 2023})

    await note_service.shelf_repository.create({"user_id": user.id, "book_id": book.id})

    await note_service.note_repository.create({"user_id": user.id, "book_id": book.id, "text": "Test note", "page": 10})

    with pytest.raises(HTTPException) as exc_info:
        await note_service.get_by_id(user.id, book.id, 99999)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_note_service_update_happy_path(note_service):
    """Тест частичного обновления заметки. Обновляет заметку и проверяет, что она действительно обновлена."""
    user = await note_service.user_repository.create(
        {"username": "test_user", "email": "test_email@example.com", "password_hash": "test_password"}
    )

    book = await note_service.book_repository.create({"title": "Test Book", "release_year": 2023})

    await note_service.shelf_repository.create({"user_id": user.id, "book_id": book.id})

    note = await note_service.note_repository.create(
        {"user_id": user.id, "book_id": book.id, "text": "Test note", "page": 10}
    )

    note_update = NoteUpdate(text="Updated note")
    updated_note = await note_service.update(user.id, book.id, note.id, note_update)

    assert (
        updated_note.id == note.id
        and updated_note.text == note_update.text
        and updated_note.page == note.page
        and updated_note.book_id == note.book_id
        and updated_note.user_id == note.user_id
    )


@pytest.mark.asyncio
async def test_note_service_update_not_found_raises_404(note_service):
    """Тест частичного обновления заметки, которой не существует. Вызывает исключение 404."""
    user = await note_service.user_repository.create(
        {"username": "test_user", "email": "test_email@example.com", "password_hash": "test_password"}
    )

    book = await note_service.book_repository.create({"title": "Test Book", "release_year": 2023})

    await note_service.shelf_repository.create({"user_id": user.id, "book_id": book.id})

    await note_service.note_repository.create({"user_id": user.id, "book_id": book.id, "text": "Test note", "page": 10})

    note_update = NoteUpdate(text="Updated note")
    with pytest.raises(HTTPException) as exc_info:
        await note_service.update(user.id, book.id, 99999, note_update)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_note_service_replace_happy_path(note_service):
    """Тест полного обновления заметки. Обновляет заметку и проверяет, что она действительно обновлена."""
    user = await note_service.user_repository.create(
        {"username": "test_user", "email": "test_email@example.com", "password_hash": "test_password"}
    )

    book = await note_service.book_repository.create({"title": "Test Book", "release_year": 2023})

    await note_service.shelf_repository.create({"user_id": user.id, "book_id": book.id})

    note = await note_service.note_repository.create(
        {"user_id": user.id, "book_id": book.id, "text": "Test note", "page": 10}
    )

    note_create = NoteCreate(text="Updated note", page=20)
    replaced_note = await note_service.replace(user.id, book.id, note.id, note_create)
    assert (
        replaced_note.id == note.id
        and replaced_note.text == note_create.text
        and replaced_note.page == note_create.page
        and replaced_note.book_id == note.book_id
        and replaced_note.user_id == note.user_id
    )


@pytest.mark.asyncio
async def test_note_service_replace_not_found_raises_404(note_service):
    """Тест полного обновления заметки, которой не существует. Вызывает исключение 404."""
    user = await note_service.user_repository.create(
        {"username": "test_user", "email": "test_email@example.com", "password_hash": "test_password"}
    )

    book = await note_service.book_repository.create({"title": "Test Book", "release_year": 2023})

    await note_service.shelf_repository.create({"user_id": user.id, "book_id": book.id})

    await note_service.note_repository.create({"user_id": user.id, "book_id": book.id, "text": "Test note", "page": 10})

    note_create = NoteCreate(text="Updated note", page=20)
    with pytest.raises(HTTPException) as exc_info:
        await note_service.replace(user.id, book.id, 99999, note_create)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_note_service_delete_happy_path(note_service):
    """Тест удаления заметки. Удаляет заметку и проверяет, что она действительно удалена."""
    user = await note_service.user_repository.create(
        {"username": "test_user", "email": "test_email@example.com", "password_hash": "test_password"}
    )

    book = await note_service.book_repository.create({"title": "Test Book", "release_year": 2023})

    await note_service.shelf_repository.create({"user_id": user.id, "book_id": book.id})

    note = await note_service.note_repository.create(
        {"user_id": user.id, "book_id": book.id, "text": "Test note", "page": 10}
    )

    await note_service.delete(user.id, book.id, note.id)
    # Проверяем, что заметка действительно удалена
    with pytest.raises(HTTPException) as exc_info:
        await note_service.get_by_id(user.id, book.id, note.id)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_note_service_delete_not_found_raises_404(note_service):
    """Тест удаления заметки, которой не существует. Вызывает исключение 404."""
    user = await note_service.user_repository.create(
        {"username": "test_user", "email": "test_email@example.com", "password_hash": "test_password"}
    )

    book = await note_service.book_repository.create({"title": "Test Book", "release_year": 2023})

    await note_service.shelf_repository.create({"user_id": user.id, "book_id": book.id})

    await note_service.note_repository.create({"user_id": user.id, "book_id": book.id, "text": "Test note", "page": 10})

    with pytest.raises(HTTPException) as exc_info:
        await note_service.delete(user.id, book.id, 99999)
    assert exc_info.value.status_code == 404
