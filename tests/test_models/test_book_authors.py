import pytest
from sqlalchemy.exc import IntegrityError

from app.models.authors import Author
from app.models.book_authors import BookAuthor
from app.models.books import Book


@pytest.fixture
async def book(db_session):
    """Создает книгу в базе данных."""
    book = Book(title="Test Book", release_year=2023)
    db_session.add(book)
    await db_session.commit()
    await db_session.refresh(book)
    return book


@pytest.fixture
async def author(db_session):
    """Cоздает автора в базе данных."""
    author = Author(fullname="Test Author", birth_year=1990, death_year=2023)
    db_session.add(author)
    await db_session.commit()
    await db_session.refresh(author)
    return author


@pytest.mark.asyncio
async def test_book_author_relationship(db_session, book, author):
    """Тестирует связь между книгой и автором с корректными данными."""
    link = BookAuthor(book_id=book.id, author_id=author.id)

    db_session.add(link)
    await db_session.commit()

    assert link.book_id == book.id
    assert link.author_id == author.id
    assert link.created_at is not None


@pytest.mark.asyncio
async def test_insert_book_author_with_incorrect_book_id_raises_integrity_error(db_session, author):
    """Тестирует вставку книги с несуществующим book_id."""
    link = BookAuthor(book_id=999999, author_id=author.id)
    db_session.add(link)

    with pytest.raises(IntegrityError):
        await db_session.commit()


@pytest.mark.asyncio
async def test_insert_book_author_with_incorrect_author_id_raises_integrity_error(db_session, book):
    """Тестирует вставку книги с несуществующим author_id."""
    link = BookAuthor(book_id=book.id, author_id=999999)
    db_session.add(link)

    with pytest.raises(IntegrityError):
        await db_session.commit()


@pytest.mark.asyncio
async def test_insert_book_author_unique_constraint(db_session, book, author):
    """Тестирует уникальность связки book_id и author_id."""
    link1 = BookAuthor(book_id=book.id, author_id=author.id)
    link2 = BookAuthor(book_id=book.id, author_id=author.id)
    db_session.add_all([link1, link2])

    with pytest.raises(IntegrityError):
        await db_session.commit()


@pytest.mark.asyncio
async def test_book_author_delete_book_raises_integrity_error(db_session, book, author):
    """Тестирует удаление книги, на которую ссылается автор."""
    link = BookAuthor(book_id=book.id, author_id=author.id)

    db_session.add(link)
    await db_session.commit()

    await db_session.delete(book)
    with pytest.raises(IntegrityError):
        await db_session.commit()


@pytest.mark.asyncio
async def test_book_author_delete_author_raises_integrity_error(db_session, book, author):
    """Тестирует удаление автора, на которого ссылается книга."""
    link = BookAuthor(book_id=book.id, author_id=author.id)

    db_session.add(link)
    await db_session.commit()

    await db_session.delete(author)
    with pytest.raises(IntegrityError):
        await db_session.commit()
