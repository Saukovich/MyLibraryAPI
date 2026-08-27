import pytest

from app.models.books import Book
from app.models.user_books import UserBook
from app.models.users import User
from app.repositories.note_repository import NoteRepository
from app.schemas.params import NoteFilterParams


@pytest.fixture
def note_repository(db_session):
    """Фикстура для создания экземпляра NoteRepository."""
    note_repository = NoteRepository(db_session)
    return note_repository


@pytest.fixture
async def user_book(db_session):
    """Фикстура для создания UserBook."""
    user = User(username="test_user", email="testuser@gmail.com", password_hash="test_password")
    book = Book(title="test_book", release_year=2026)
    db_session.add_all([user, book])
    await db_session.flush()

    user_book = UserBook(user_id=user.id, book_id=book.id)
    db_session.add(user_book)
    await db_session.flush()
    await db_session.refresh(user_book)

    return user_book


# =======================================
# get_by_shelf_entry (с одним параметром)
# =======================================


@pytest.mark.asyncio
async def test_note_repo_get_by_shelf_entry_page_min_field(note_repository, user_book):
    """Тест для проверки фильтрации по page_min."""
    await note_repository.create({"user_id": user_book.user_id, "book_id": user_book.book_id, "text": "", "page": 10})
    await note_repository.create({"user_id": user_book.user_id, "book_id": user_book.book_id, "text": "", "page": 8})
    await note_repository.create({"user_id": user_book.user_id, "book_id": user_book.book_id, "text": "", "page": 1})

    notes = await note_repository.get_by_shelf_entry(
        user_book.user_id, user_book.book_id, NoteFilterParams(page_min=10)
    )
    assert len(notes) == 1


@pytest.mark.asyncio
async def test_note_repo_get_by_shelf_entry_page_max_field(note_repository, user_book):
    """Тест для проверки фильтрации по page_max."""
    await note_repository.create({"user_id": user_book.user_id, "book_id": user_book.book_id, "text": "", "page": 10})
    await note_repository.create({"user_id": user_book.user_id, "book_id": user_book.book_id, "text": "", "page": 8})
    await note_repository.create({"user_id": user_book.user_id, "book_id": user_book.book_id, "text": "", "page": 1})

    notes = await note_repository.get_by_shelf_entry(user_book.user_id, user_book.book_id, NoteFilterParams(page_max=8))
    assert len(notes) == 2


# ========================================
# get_by_shelf_entry (с двумя параметрами)
# ========================================


@pytest.mark.asyncio
async def test_note_repo_get_by_shelf_entry_page_range(note_repository, user_book):
    """Тест для проверки фильтрации по диапазону страниц."""
    await note_repository.create({"user_id": user_book.user_id, "book_id": user_book.book_id, "text": "", "page": 10})
    await note_repository.create({"user_id": user_book.user_id, "book_id": user_book.book_id, "text": "", "page": 8})
    await note_repository.create({"user_id": user_book.user_id, "book_id": user_book.book_id, "text": "", "page": 1})

    notes = await note_repository.get_by_shelf_entry(
        user_book.user_id, user_book.book_id, NoteFilterParams(page_min=1, page_max=8)
    )

    assert len(notes) == 2


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "sort_by,order_by",
    [
        ("id", "asc"),
        ("id", "desc"),
        ("page", "asc"),
        ("page", "desc"),
        ("text", "asc"),
        ("text", "desc"),
        ("created_at", "asc"),
        ("created_at", "desc"),
    ],
)
async def test_note_repo_get_by_shelf_entry_sort_by_order_by(note_repository, user_book, sort_by, order_by):
    """Тест для проверки сортировки по полям."""
    await note_repository.create({"user_id": user_book.user_id, "book_id": user_book.book_id, "text": "a", "page": 10})
    await note_repository.create({"user_id": user_book.user_id, "book_id": user_book.book_id, "text": "b", "page": 8})
    await note_repository.create({"user_id": user_book.user_id, "book_id": user_book.book_id, "text": "c", "page": 1})

    note_filter_params = NoteFilterParams(sort_by=sort_by, order_by=order_by)
    notes = await note_repository.get_by_shelf_entry(user_book.user_id, user_book.book_id, note_filter_params)

    # Проверяем, что количество записей соответствует ожидаемому
    for i in range(1, len(notes)):
        # Если порядок не соответствует ожидаемому, то тест провален
        if order_by == "asc" and notes[i - 1].__getattribute__(sort_by) > notes[i].__getattribute__(sort_by):
            assert False
        elif order_by == "desc" and notes[i - 1].__getattribute__(sort_by) < notes[i].__getattribute__(sort_by):
            assert False

    assert True  # Если мы дошли до этого места, значит сортировка прошла успешно
