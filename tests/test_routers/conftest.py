import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.security import hash_password
from app.main import app
from app.models.authors import Author
from app.models.books import Book
from app.models.notes import Note
from app.models.user_books import UserBook
from app.models.users import User


@pytest.fixture
async def existing_user(db_session):
    """Фикстура для пользователя, существующего в базе данных."""
    user = User(username="test", email="test@example.com", password_hash=hash_password("testtest"))
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
async def client(db_session):
    """Фикстура для HTTP-клиента с переопределенным get_db."""

    async def override_get_db():
        yield db_session

    # Перезаписываем зависимость get_db
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()  # Очищаем зависимости после выполнения тестов


@pytest.fixture
async def authenticated_client(client, existing_user):
    """Фикстура для HTTP-клиента с авторизацией."""

    async def override_get_current_user():
        return existing_user

    # Перезаписываем зависимость get_current_user
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield client
    app.dependency_overrides.clear()  # Очищаем зависимости после выполнения тестов


@pytest.fixture
async def author(db_session):
    """Фикстура для автора."""
    author = Author(fullname="Test Author", birth_year=1990, death_year=2020)
    db_session.add(author)
    await db_session.flush()
    await db_session.refresh(author)
    return author


@pytest.fixture
async def book(db_session, author):
    """Фикстура для книги."""
    book = Book(title="Test Book", release_year=2020)
    book.authors = [author]
    db_session.add(book)
    await db_session.flush()
    await db_session.refresh(book)
    return book


@pytest.fixture
async def book_not_in_shelf(db_session, author):
    """Фикстура для книги, не находящейся на полке."""
    book = Book(title="Test Book not in shelf", release_year=2020)
    book.authors = [author]
    db_session.add(book)
    await db_session.flush()
    await db_session.refresh(book)
    return book


@pytest.fixture
async def shelf_entry(db_session, existing_user, book):
    """Фикстура для записи на полке."""
    shelf_entry = UserBook(user_id=existing_user.id, book_id=book.id)
    db_session.add(shelf_entry)
    await db_session.flush()
    await db_session.refresh(shelf_entry)
    return shelf_entry


@pytest.fixture
async def note(db_session, existing_user, book, shelf_entry):
    """Фикстура для заметки."""
    note = Note(user_id=existing_user.id, book_id=book.id, text="Test Note", page=1)
    db_session.add(note)
    await db_session.flush()
    await db_session.refresh(note)
    return note
