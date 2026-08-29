from datetime import datetime, timedelta

import pytest

from app.models.authors import Author
from app.models.books import Book
from app.models.enums import BookStatus
from app.models.users import User
from app.repositories.shelf_repository import ShelfRepository
from app.schemas.params import ShelfFilterParams


@pytest.fixture
def shelf_repository(db_session):
    """Фикстура для ShelfRepository."""
    return ShelfRepository(db_session)


# ==============================================================
# get_by_filters (параметры, унаследованные от BookFilterParams)
# ==============================================================


@pytest.mark.asyncio
async def test_shelf_repo_get_by_filters_title(shelf_repository):
    """Тестирует фильтрацию по названию."""
    book = Book(title="Test Book", release_year=2023)
    shelf_repository.session.add(book)
    await shelf_repository.session.flush()

    user = User(username="testuser", email="testuser@example.com", password_hash="password123")
    shelf_repository.session.add(user)
    await shelf_repository.session.flush()

    await shelf_repository.create({"user_id": user.id, "book_id": book.id})
    shelf_entry = await shelf_repository.get_by_filters(user.id, ShelfFilterParams(title="book"))

    assert len(shelf_entry) == 1 and shelf_entry[0].book_id == book.id and shelf_entry[0].user_id == user.id


@pytest.mark.asyncio
async def test_shelf_repo_get_by_filters_author_id(shelf_repository):
    """Тестирует фильтрацию по id автора."""
    book = Book(title="Test Book", release_year=2023)
    book.authors = []
    shelf_repository.session.add(book)
    await shelf_repository.session.flush()

    author = Author(fullname="Test Author", birth_year=1990)
    shelf_repository.session.add(author)
    await shelf_repository.session.flush()

    book.authors.append(author)
    await shelf_repository.session.flush()

    user = User(username="testuser", email="testuser@example.com", password_hash="password123")
    shelf_repository.session.add(user)
    await shelf_repository.session.flush()

    await shelf_repository.create({"user_id": user.id, "book_id": book.id})
    shelf_entry = await shelf_repository.get_by_filters(user.id, ShelfFilterParams(author_id=author.id))

    assert (
        len(shelf_entry) == 1
        and shelf_entry[0].book_id == book.id
        and shelf_entry[0].user_id == user.id
        and shelf_entry[0].book.authors[0].id == author.id
    )


@pytest.mark.asyncio
async def test_shelf_repo_get_by_filters_author_name(shelf_repository):
    """Тестирует фильтрацию по имени автора."""
    book = Book(title="Test Book", release_year=2023)
    book.authors = []
    shelf_repository.session.add(book)
    await shelf_repository.session.flush()

    author = Author(fullname="Test Author", birth_year=1990)
    shelf_repository.session.add(author)
    await shelf_repository.session.flush()

    book.authors.append(author)
    await shelf_repository.session.flush()

    user = User(username="testuser", email="testuser@example.com", password_hash="password123")
    shelf_repository.session.add(user)
    await shelf_repository.session.flush()

    await shelf_repository.create({"user_id": user.id, "book_id": book.id})
    shelf_entry = await shelf_repository.get_by_filters(user.id, ShelfFilterParams(author_name=author.fullname))

    assert (
        len(shelf_entry) == 1
        and shelf_entry[0].book_id == book.id
        and shelf_entry[0].user_id == user.id
        and shelf_entry[0].book.authors[0].id == author.id
        and shelf_entry[0].book.authors[0].fullname.lower() in author.fullname.lower()
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("release_year_min, release_year_max", [(2023, None), (None, 2023), (2023, 2023)])
async def test_shelf_repo_get_by_filters_release_year(shelf_repository, release_year_min, release_year_max):
    """Тестирует фильтрацию по году выпуска."""
    book = Book(title="Test Book", release_year=2023)
    shelf_repository.session.add(book)
    await shelf_repository.session.flush()

    user = User(username="testuser", email="testuser@example.com", password_hash="password123")
    shelf_repository.session.add(user)
    await shelf_repository.session.flush()

    await shelf_repository.create({"user_id": user.id, "book_id": book.id})
    shelf_entry = await shelf_repository.get_by_filters(
        user.id, ShelfFilterParams(release_year_min=release_year_min, release_year_max=release_year_max)
    )

    assert (
        len(shelf_entry) == 1
        and shelf_entry[0].book_id == book.id
        and shelf_entry[0].user_id == user.id
        and shelf_entry[0].book.release_year >= (release_year_min or 0)
        and shelf_entry[0].book.release_year <= (release_year_max or 9999)
    )


@pytest.mark.asyncio
async def test_shelf_repo_get_by_filters_one_author(shelf_repository):
    """Тестирует фильтрацию по одному автору."""
    book1 = Book(title="Test Book", release_year=2023)
    book2 = Book(title="Test Book 2", release_year=2023)
    book1.authors = []
    book2.authors = []
    shelf_repository.session.add_all([book1, book2])
    await shelf_repository.session.flush()

    author1 = Author(fullname="Test Author", birth_year=1990)
    author2 = Author(fullname="Test Author 2", birth_year=1990)
    shelf_repository.session.add(author1, author2)
    await shelf_repository.session.flush()

    book1.authors.append(author1)
    book2.authors.extend([author1, author2])
    await shelf_repository.session.flush()

    user = User(username="testuser", email="testuser@example.com", password_hash="password123")
    shelf_repository.session.add(user)
    await shelf_repository.session.flush()

    await shelf_repository.create({"user_id": user.id, "book_id": book1.id})
    await shelf_repository.create({"user_id": user.id, "book_id": book2.id})
    shelf_entry = await shelf_repository.get_by_filters(user.id, ShelfFilterParams(one_author=True))

    assert (
        len(shelf_entry) == 1
        and shelf_entry[0].book_id == book1.id
        and shelf_entry[0].user_id == user.id
        and len(shelf_entry[0].book.authors) == 1
        and shelf_entry[0].book.authors[0].id == author1.id
    )


# ===============================================
# get_by_filters (Параметры от ShelfFilterParams)
# ===============================================


@pytest.mark.asyncio
@pytest.mark.parametrize("status", [BookStatus.READING, BookStatus.READ, BookStatus.ABANDONED])
async def test_shelf_repo_get_by_filters_(shelf_repository, status):
    """Тестирует фильтрацию по статусу."""
    book1 = Book(title="Test Book", release_year=2023)
    book2 = Book(title="Test Book 2", release_year=2023)
    shelf_repository.session.add_all([book1, book2])
    await shelf_repository.session.flush()

    user = User(username="testuser", email="testuser@example.com", password_hash="password123")
    shelf_repository.session.add(user)
    await shelf_repository.session.flush()

    await shelf_repository.create({"user_id": user.id, "book_id": book1.id, "status": status})
    await shelf_repository.create({"user_id": user.id, "book_id": book2.id})
    shelf_entry = await shelf_repository.get_by_filters(user.id, ShelfFilterParams(status=status))

    assert (
        len(shelf_entry) == 1
        and shelf_entry[0].book_id == book1.id
        and shelf_entry[0].user_id == user.id
        and shelf_entry[0].status == status
    )


@pytest.mark.asyncio
async def test_shelf_repo_get_by_filters_min_rating(shelf_repository):
    """Тестирует фильтрацию по рейтингу."""
    book1 = Book(title="Test Book", release_year=2023)
    book2 = Book(title="Test Book 2", release_year=2023)
    shelf_repository.session.add_all([book1, book2])
    await shelf_repository.session.flush()

    user = User(username="testuser", email="testuser@example.com", password_hash="password123")
    shelf_repository.session.add(user)
    await shelf_repository.session.flush()

    await shelf_repository.create({"user_id": user.id, "book_id": book1.id, "rating": 5})
    await shelf_repository.create({"user_id": user.id, "book_id": book2.id, "rating": 8})
    shelf_entry = await shelf_repository.get_by_filters(user.id, ShelfFilterParams(min_rating=8))

    assert (
        len(shelf_entry) == 1
        and shelf_entry[0].book_id == book2.id
        and shelf_entry[0].user_id == user.id
        and shelf_entry[0].rating >= 8
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "added_at_min,added_at_max",
    [
        (datetime(year=2026, month=8, day=29), None),
        (None, datetime.now() + timedelta(days=1)),
        (datetime(year=2026, month=8, day=29), datetime.now() + timedelta(days=1)),
    ],
)
async def test_shelf_repo_get_by_filters_added_at_min_max(shelf_repository, added_at_min, added_at_max):
    """Тестирует фильтрацию по дате добавления."""
    book1 = Book(title="Test Book", release_year=2023)
    shelf_repository.session.add(book1)
    await shelf_repository.session.flush()

    user = User(username="testuser", email="testuser@example.com", password_hash="password123")
    shelf_repository.session.add(user)
    await shelf_repository.session.flush()

    await shelf_repository.create({"user_id": user.id, "book_id": book1.id, "rating": 5})
    shelf_entry = await shelf_repository.get_by_filters(
        user.id, ShelfFilterParams(added_at_min=added_at_min, added_at_max=added_at_max)
    )

    assert (
        len(shelf_entry) == 1
        and shelf_entry[0].book_id == book1.id
        and shelf_entry[0].user_id == user.id
        and shelf_entry[0].added_at >= (added_at_min or datetime.min)
        and shelf_entry[0].added_at <= (added_at_max or datetime.max)
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "sort_by,order_by",
    [
        ("book_id", "asc"),
        ("book_id", "desc"),
        ("title", "asc"),
        ("title", "desc"),
        ("release_year", "asc"),
        ("release_year", "desc"),
        ("author_id", "asc"),
        ("author_id", "desc"),
        ("rating", "asc"),
        ("rating", "desc"),
    ],
)
async def test_shelf_repo_get_by_filters_sort_by_order_by(shelf_repository, sort_by, order_by):
    """Тестирует сортировку и порядок сортировки."""
    book1 = Book(title="Test Book", release_year=2021)
    book2 = Book(title="Test Book 2", release_year=2022)
    book3 = Book(title="Test Book 3", release_year=2023)
    book1.authors = []
    book2.authors = []
    book3.authors = []
    shelf_repository.session.add_all([book1, book2, book3])
    await shelf_repository.session.flush()

    author1 = Author(fullname="Test Author", birth_year=1990)
    author2 = Author(fullname="Test Author 2", birth_year=1990)
    author3 = Author(fullname="Test Author 3", birth_year=1990)
    shelf_repository.session.add_all([author1, author2, author3])
    await shelf_repository.session.flush()

    book1.authors.append(author1)
    book2.authors.append(author2)
    book3.authors.append(author3)
    await shelf_repository.session.flush()

    user = User(username="testuser", email="testuser@example.com", password_hash="password123")
    shelf_repository.session.add(user)
    await shelf_repository.session.flush()

    await shelf_repository.create({"user_id": user.id, "book_id": book1.id, "rating": 5})
    await shelf_repository.create({"user_id": user.id, "book_id": book2.id, "rating": 8, "status": BookStatus.READING})
    await shelf_repository.create({"user_id": user.id, "book_id": book3.id, "rating": 10, "status": BookStatus.READ})
    shelf_entry = await shelf_repository.get_by_filters(user.id, ShelfFilterParams(sort_by=sort_by, order_by=order_by))

    for i in range(1, len(shelf_entry)):
        if order_by == "asc":
            if hasattr(shelf_entry[i], sort_by) and getattr(shelf_entry[i], sort_by) < getattr(
                shelf_entry[i - 1], sort_by
            ):
                assert False
            elif hasattr(shelf_entry[i].book, sort_by) and getattr(shelf_entry[i].book, sort_by) < getattr(
                shelf_entry[i - 1].book, sort_by
            ):
                assert False
            elif hasattr(shelf_entry[i].book.authors[0], sort_by) and getattr(
                shelf_entry[i].book.authors[0], sort_by
            ) < getattr(shelf_entry[i - 1].book.authors[0], sort_by):
                assert False
        elif order_by == "desc":
            if hasattr(shelf_entry[i], sort_by) and getattr(shelf_entry[i], sort_by) > getattr(
                shelf_entry[i - 1], sort_by
            ):
                assert False
            elif hasattr(shelf_entry[i].book, sort_by) and getattr(shelf_entry[i].book, sort_by) > getattr(
                shelf_entry[i - 1].book, sort_by
            ):
                assert False
            elif hasattr(shelf_entry[i].book.authors[0], sort_by) and getattr(
                shelf_entry[i].book.authors[0], sort_by
            ) > getattr(shelf_entry[i - 1].book.authors[0], sort_by):
                assert False

    assert len(shelf_entry) == 3 and True


# =========
# get_stats
# =========


@pytest.mark.asyncio
async def test_shelf_repo_get_stats(shelf_repository):
    """Тестирует получение статистики по полке пользователя."""
    book1 = Book(title="Test Book", release_year=2023)
    book2 = Book(title="Test Book 2", release_year=2023)
    book3 = Book(title="Test Book 3", release_year=2023)
    book1.authors = []
    book2.authors = []
    book3.authors = []
    shelf_repository.session.add_all([book1, book2, book3])
    await shelf_repository.session.flush()

    author1 = Author(fullname="Test Author", birth_year=1990)
    author2 = Author(fullname="Test Author 2", birth_year=1990)
    shelf_repository.session.add(author1, author2)
    await shelf_repository.session.flush()

    book1.authors.append(author1)
    book2.authors.extend([author1, author2])
    book3.authors.append(author1)
    await shelf_repository.session.flush()

    user = User(username="testuser", email="testuser@example.com", password_hash="password123")
    shelf_repository.session.add(user)
    await shelf_repository.session.flush()

    await shelf_repository.create({"user_id": user.id, "book_id": book1.id, "rating": 5})
    await shelf_repository.create({"user_id": user.id, "book_id": book2.id, "rating": 3})
    await shelf_repository.create({"user_id": user.id, "book_id": book3.id, "rating": 10})

    book_stats = await shelf_repository.get_stats(user.id)
    assert (
        book_stats.number_of_books == 3
        and book_stats.avg_rating == 6.0
        and book_stats.favorite_author == author1.fullname
    )


# =============================
# exists_by_user_id_and_book_id
# =============================


@pytest.mark.asyncio
async def test_shelf_repo_exists_by_user_id_and_book_id(shelf_repository):
    """Тестирует проверку существования записи на полке пользователя по id книги."""
    book = Book(title="Test Book", release_year=2023)
    shelf_repository.session.add(book)
    await shelf_repository.session.flush()

    user = User(username="testuser", email="testuser@example.com", password_hash="password123")
    shelf_repository.session.add(user)
    await shelf_repository.session.flush()

    await shelf_repository.create({"user_id": user.id, "book_id": book.id})
    assert await shelf_repository.exists_by_user_id_and_book_id(user.id, book.id) is True
