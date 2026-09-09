import pytest

from app.models.authors import Author
from app.models.user_books import UserBook
from app.models.users import User
from app.repositories.book_repository import BookRepository
from app.schemas.params import BookFilterParams


@pytest.fixture
def book_repository(db_session):
    """Фикстура для создания экземпляра BookRepository."""
    return BookRepository(db_session)


# =========
# get_by_id
# =========


@pytest.mark.asyncio
async def test_book_repo_get_by_id_with_correct_id(book_repository):
    """Тестирование метода get_by_id с корректным id."""
    await book_repository.create({"title": "Test Book", "release_year": 2023})
    book = await book_repository.get_by_id(id=1)
    assert book.title == "Test Book" and book.release_year == 2023 and book.id == 1


@pytest.mark.asyncio
async def test_book_repo_get_by_id_with_incorrect_id(book_repository):
    """Тестирование метода get_by_id с некорректным id."""
    book = await book_repository.get_by_id(id=100)
    assert book is None


# ===================================
# get_by_filters (С одним параметром)
# ===================================


@pytest.mark.asyncio
async def test_book_repo_get_by_filters_with_title_exist(book_repository):
    """Тестирование метода get_by_filters с параметром title."""
    await book_repository.create({"title": "Test Book title", "release_year": 2023})
    await book_repository.create({"title": "Test Book TITLE", "release_year": 2023})
    await book_repository.create({"title": "Test Book tItle", "release_year": 2023})
    await book_repository.create({"title": "Test Book titLE", "release_year": 2023})

    books = await book_repository.get_by_filters(BookFilterParams(title="title"))
    assert len(books) == 4


@pytest.mark.asyncio
async def test_book_repo_get_by_filters_with_title_not_exist(book_repository):
    """Тестирование метода get_by_filters с параметром title."""
    await book_repository.create({"title": "Test Book 1", "release_year": 2023})
    await book_repository.create({"title": "Test Book 2", "release_year": 2023})
    await book_repository.create({"title": "Test Book 3", "release_year": 2023})
    await book_repository.create({"title": "Test Book 4", "release_year": 2023})

    books = await book_repository.get_by_filters(BookFilterParams(title="title"))
    assert len(books) == 0


@pytest.mark.asyncio
async def test_book_repo_get_by_filters_with_author_id(book_repository):
    """Тестирование метода get_by_filters с параметром author_id."""
    book = await book_repository.create({"title": "Test Book 1", "release_year": 2023})
    authors = [Author(fullname="Test Author", birth_year=1990)]
    await book_repository.set_authors(book, authors)

    books = await book_repository.get_by_filters(BookFilterParams(author_id=1))
    assert len(books) == 1


@pytest.mark.asyncio
async def test_book_repo_get_by_filters_with_author_name(book_repository):
    """Тестирование метода get_by_filters с параметром author_name."""
    book = await book_repository.create({"title": "Test Book 1", "release_year": 2023})
    authors = [Author(fullname="Test Author", birth_year=1990)]
    await book_repository.set_authors(book, authors)

    books = await book_repository.get_by_filters(BookFilterParams(author_name="Author"))
    assert len(books) == 1


@pytest.mark.asyncio
async def test_book_repo_get_by_filters_with_one_author(book_repository):
    """Тестирование метода get_by_filters с параметром one_author."""
    book1 = await book_repository.create({"title": "Test Book 1", "release_year": 2023})
    book2 = await book_repository.create({"title": "Test Book 2", "release_year": 2023})
    book3 = await book_repository.create({"title": "Test Book 3", "release_year": 2023})

    await book_repository.set_authors(book1, [Author(fullname="Test Author", birth_year=1990)])
    await book_repository.set_authors(
        book2,
        [
            Author(fullname="Test Author", birth_year=1990),
            Author(fullname="Test Author 2", birth_year=1990),
        ],
    )
    await book_repository.set_authors(book3, [Author(fullname="Test Author", birth_year=1990)])

    books = await book_repository.get_by_filters(BookFilterParams(one_author=True))
    assert len(books) == 2


@pytest.mark.asyncio
async def test_book_repo_get_by_filters_with_release_year_min(book_repository):
    """Тестирование метода get_by_filters с параметром release_year_min."""
    await book_repository.create({"title": "Test Book 1", "release_year": 2023})
    await book_repository.create({"title": "Test Book 2", "release_year": 2024})
    await book_repository.create({"title": "Test Book 3", "release_year": 2025})

    books = await book_repository.get_by_filters(BookFilterParams(release_year_min=2024))
    assert len(books) == 2


@pytest.mark.asyncio
async def test_book_repo_get_by_filters_with_release_year_max(book_repository):
    """Тестирование метода get_by_filters с параметром release_year_max."""
    await book_repository.create({"title": "Test Book 1", "release_year": 2023})
    await book_repository.create({"title": "Test Book 2", "release_year": 2024})
    await book_repository.create({"title": "Test Book 3", "release_year": 2025})

    books = await book_repository.get_by_filters(BookFilterParams(release_year_max=2024))
    assert len(books) == 2


@pytest.mark.asyncio
async def test_book_repo_get_by_filters_with_release_year_min_and_max(book_repository):
    """Тестирование метода get_by_filters с параметрами release_year_min и release_year_max."""
    await book_repository.create({"title": "Test Book 1", "release_year": 2023})
    await book_repository.create({"title": "Test Book 2", "release_year": 2024})
    await book_repository.create({"title": "Test Book 3", "release_year": 2025})

    books = await book_repository.get_by_filters(BookFilterParams(release_year_min=2024, release_year_max=2024))
    assert len(books) == 1


# ==========================================
# get_by_filters (С несколькими параметрами)
# ==========================================


@pytest.mark.asyncio
async def test_book_repo_get_by_filters_with_author_id_and_title(book_repository):
    """Тестирование метода get_by_filters с параметрами author_id и title."""
    book1 = await book_repository.create({"title": "Test Book 1", "release_year": 2023})
    authors = [Author(fullname="Test Author", birth_year=1990)]
    await book_repository.set_authors(book1, authors)

    book2 = await book_repository.create({"title": "Test Book 2", "release_year": 2023})
    authors = [Author(fullname="Test Author 1", birth_year=1990)]
    await book_repository.set_authors(book2, authors)

    books = await book_repository.get_by_filters(BookFilterParams(author_id=1, title="Book"))
    assert len(books) == 1 and books[0].title == "Test Book 1" and books[0].authors[0].fullname == "Test Author"


@pytest.mark.asyncio
async def test_book_repo_get_by_filters_with_author_name_and_one_author(book_repository):
    """Тестирование метода get_by_filters с параметрами author_name и one_author."""
    book = await book_repository.create({"title": "Test Book 1", "release_year": 2023})
    authors = [Author(fullname="Test Author", birth_year=1990), Author(fullname="Test Author 1", birth_year=1990)]
    await book_repository.set_authors(book, authors)

    book = await book_repository.create({"title": "Test Book 2", "release_year": 2023})
    authors = [Author(fullname="Test Author", birth_year=1990)]
    await book_repository.set_authors(book, authors)

    books = await book_repository.get_by_filters(BookFilterParams(author_name="Author", one_author=True))
    assert len(books) == 1 and "Author" in books[0].authors[0].fullname


# ===========================
# get_by_filters (Сортировка)
# ===========================


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "sort_by,order_by", [("title", "asc"), ("title", "desc"), ("release_year", "asc"), ("release_year", "desc")]
)
async def test_book_repo_get_by_filters_with_sort_by_and_order_by(book_repository, sort_by, order_by):
    """Тестирование метода get_by_filters с параметрами sort_by и order_by."""
    await book_repository.create({"title": "Test Book 1", "release_year": 2023})
    await book_repository.create({"title": "Test Book 2", "release_year": 2024})
    await book_repository.create({"title": "Test Book 3", "release_year": 2025})

    books = await book_repository.get_by_filters(BookFilterParams(sort_by=sort_by, order_by=order_by))

    for i in range(1, len(books)):
        if order_by == "asc" and books[i].__getattribute__(sort_by) < books[i - 1].__getattribute__(sort_by):
            assert False
        elif order_by == "desc" and books[i].__getattribute__(sort_by) > books[i - 1].__getattribute__(sort_by):
            assert False

    assert True  # Проверка, что цикл завершился без ошибок


# ===============
# exists_by_title
# ===============


@pytest.mark.asyncio
async def test_book_repo_exists_by_title(book_repository):
    """Тестирование метода exists_by_title."""
    await book_repository.create({"title": "Test Book", "release_year": 2023})

    result1 = await book_repository.exists_by_title("Test Book")
    result2 = await book_repository.exists_by_title("Book")
    result3 = await book_repository.exists_by_title("Kniga")

    assert result1 is True and result2 is False and result3 is False


# ===========
# get_popular
# ===========


@pytest.mark.asyncio
async def test_book_repo_get_popular(book_repository, db_session):
    """Тестирование метода get_popular."""
    book1 = await book_repository.create({"title": "Test Book 1", "release_year": 2023})
    book2 = await book_repository.create({"title": "Test Book 2", "release_year": 2024})
    await book_repository.create({"title": "Test Book 3", "release_year": 2025})

    user1 = User(username="user1", email="user1@gmail.com", password_hash="password")
    user2 = User(username="user2", email="user2@gmail.com", password_hash="password")

    db_session.add_all([user1, user2])
    await db_session.flush()

    user_book1 = UserBook(book_id=book1.id, user_id=user1.id, rating=5)
    user_book2 = UserBook(book_id=book2.id, user_id=user1.id, rating=4)

    user_book3 = UserBook(book_id=book1.id, user_id=user2.id, rating=3)

    db_session.add_all([user_book1, user_book2, user_book3])
    await db_session.flush()

    popular_books = await book_repository.get_popular()
    assert (
        len(popular_books) == 2  # Должно быть 2 книги
        and popular_books[0].book.id == book1.id
        and popular_books[1].book.id == book2.id  # Проверка id книг
        and popular_books[0].avg_rating == 4.0
        and popular_books[1].avg_rating == 4  # Проверка среднего рейтинга
    )
