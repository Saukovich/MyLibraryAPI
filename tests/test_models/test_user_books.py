import pytest
from sqlalchemy.exc import IntegrityError

from app.models.books import Book
from app.models.enums import BookStatus
from app.models.user_books import UserBook
from app.models.users import User


@pytest.fixture
async def user(db_session):
    """Создает пользователя в базе данных."""
    user = User(username="test_user", email="test_email@gmail.com", password="test_password")

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest.fixture
async def book(db_session):
    """Создает книгу в базе данных."""
    book = Book(title="Test Book", release_year=2023)

    db_session.add(book)
    await db_session.commit()
    await db_session.refresh(book)

    return book


@pytest.mark.asyncio
async def test_user_book_relationship(db_session, user, book):
    """Тестирует связь между пользователем и книгой."""
    link = UserBook(user_id=user.id, book_id=book.id)

    db_session.add(link)
    await db_session.commit()
    await db_session.refresh(link)

    assert link.user_id == user.id
    assert link.book_id == book.id
    assert link.added_at is not None


@pytest.mark.asyncio
async def test_insert_user_book_with_incorrect_user_id_raises_integrity_error(db_session, book):
    """Тестирует вставку книги с некорректным user_id."""
    link = UserBook(user_id=99999, book_id=book.id)
    db_session.add(link)

    with pytest.raises(IntegrityError):
        await db_session.commit()


@pytest.mark.asyncio
async def test_insert_user_book_with_incorrect_book_id_raises_integrity_error(db_session, user):
    """Тестирует вставку книги с некорректным book_id."""
    link = UserBook(user_id=user.id, book_id=99999)
    db_session.add(link)

    with pytest.raises(IntegrityError):
        await db_session.commit()


@pytest.mark.asyncio
async def test_insert_user_book_unique_constraint(db_session, user, book):
    """Тестирует уникальность связи между пользователем и книгой."""
    link1 = UserBook(user_id=user.id, book_id=book.id)
    link2 = UserBook(user_id=user.id, book_id=book.id)

    db_session.add_all([link1, link2])

    with pytest.raises(IntegrityError):
        await db_session.commit()


@pytest.mark.asyncio
async def test_user_book_delete_user_raises_integrity_error(db_session, user, book):
    """Тестирует удаление пользователя, связанного с книгой."""
    link = UserBook(user_id=user.id, book_id=book.id)

    db_session.add(link)
    await db_session.commit()

    with pytest.raises(IntegrityError):
        await db_session.delete(user)
        await db_session.commit()


@pytest.mark.asyncio
async def test_user_book_delete_book_raises_integrity_error(db_session, user, book):
    """Тестирует удаление книги, связанного с пользователем."""
    link = UserBook(user_id=user.id, book_id=book.id)

    db_session.add(link)
    await db_session.commit()

    with pytest.raises(IntegrityError):
        await db_session.delete(book)
        await db_session.commit()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "rating,status", [(10, BookStatus.PLANNED), (5, BookStatus.READING), (0, BookStatus.READ), (None, BookStatus.READ)]
)
async def test_insert_user_book_with_correct_data(db_session, user, book, rating, status):
    """Тестирует вставку корректных данных в связь между пользователем и книгой."""
    link = UserBook(user_id=user.id, book_id=book.id, rating=rating, status=status)
    db_session.add(link)
    await db_session.commit()

    assert link.user_id == user.id
    assert link.book_id == book.id
    assert link.rating == rating
    assert link.status == status


@pytest.mark.asyncio
@pytest.mark.parametrize("rating", [-1, -11, 11, 100])
async def test_insert_user_book_with_incorrect_rating_raises_value_error(db_session, user, book, rating):
    """Тестирует вставку некорректного рейтинга."""
    with pytest.raises(ValueError):
        link = UserBook(user_id=user.id, book_id=book.id, rating=rating)
        db_session.add(link)
        await db_session.commit()


@pytest.mark.asyncio
@pytest.mark.parametrize("status", ["not_planned", "my status", "ready", "abandoned"])
async def test_insert_user_book_with_incorrect_status_raises_integrity_error(db_session, user, book, status):
    """Тестирует вставку некорректного статуса."""
    with pytest.raises(IntegrityError):
        link = UserBook(user_id=user.id, book_id=book.id, status=status)
        db_session.add(link)
        await db_session.commit()
