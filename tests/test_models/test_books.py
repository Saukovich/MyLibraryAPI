import pytest

from app.models.books import Book


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "book",
    [
        {"title": "Test Book", "release_year": 2020},
        {"title": "Test Book: Part Two", "release_year": 2021},
        {"title": "Test Book: Part Three", "release_year": 2022},
        {"title": "T" * 4, "release_year": 2023},
    ],
)
async def test_books_with_correct_data(book, db_session):
    """Тест на создание книги с корректными данными."""
    book = Book(**book)
    db_session.add(book)
    await db_session.commit()
    await db_session.refresh(book)

    assert book.id is not None
    assert book.created_at is not None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "book",
    [
        {"title": None, "release_year": None},
        {"title": "Test Book", "release_year": None},
        {"title": None, "release_year": 2020},
    ],
)
async def test_insert_book_with_null_title_or_release_year_raises_value_error(book, db_session):
    """Тест на создание книги с пустым названием или годом выпуска."""
    with pytest.raises(ValueError):
        db_session.add(Book(**book))
        await db_session.commit()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "book",
    [
        {"title": "T" * 51, "release_year": 2020},
        {"title": "T" * 100, "release_year": 2020},
        {"title": "Test Book" * 1000, "release_year": 2020},
    ],
)
async def test_insert_book_where_title_exceeds_max_length_raises_value_error(book, db_session):
    """Тест на создание книги с названием длиннее 50 символов."""
    with pytest.raises(ValueError):
        db_session.add(Book(**book))
        await db_session.commit()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "book",
    [
        {"title": "Test Book", "release_year": 0},
        {"title": "Test Book", "release_year": -1},
        {"title": "Test Book", "release_year": -1000},
    ],
)
async def test_insert_book_with_release_year_less_zero_raises_value_error(book, db_session):
    """Тест на создание книги с отрицательным или нулевым годом выпуска."""
    with pytest.raises(ValueError):
        db_session.add(Book(**book))
        await db_session.commit()
