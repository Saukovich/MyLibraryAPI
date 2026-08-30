from datetime import datetime
from types import SimpleNamespace

import pytest

from app.models.enums import BookStatus
from app.schemas.shelf_schemas import ShelfEntryBase, ShelfEntryResponse, ShelfEntryUpdate


@pytest.mark.parametrize(
    "status,rating",
    [(BookStatus.PLANNED, None), (BookStatus.READING, None), (BookStatus.READ, 5), (BookStatus.ABANDONED, None)],
)
def test_shelf_entry_base_check_rating_correct(status, rating):
    shelf_entry_base = ShelfEntryBase(status=status, rating=rating)
    assert shelf_entry_base.status == status and shelf_entry_base.rating is rating


@pytest.mark.parametrize(
    "status,rating",
    [
        (BookStatus.PLANNED, 5),
        (BookStatus.READING, 5),
        (BookStatus.ABANDONED, 5),
    ],
)
def test_shelf_entry_base_check_rating_incorrect(status, rating):
    with pytest.raises(ValueError):
        ShelfEntryBase(status=status, rating=rating)


def test_shelf_entry_response_flatten_shelf_entry():
    fake_author = SimpleNamespace(fullname="Fake Author")
    fake_book = SimpleNamespace(id=1, title="Fake Book", authors=[fake_author], release_year=2023)
    fake_user_book = SimpleNamespace(book=fake_book, status=BookStatus.READ, rating=5, added_at=datetime.now())
    response = ShelfEntryResponse.model_validate(fake_user_book)

    assert response.book_id == fake_user_book.book.id
    assert response.title == fake_user_book.book.title
    assert response.authors[0] == fake_user_book.book.authors[0].fullname
    assert response.release_year == fake_user_book.book.release_year
    assert response.status == fake_user_book.status and response.rating == fake_user_book.rating


@pytest.mark.parametrize(
    "status,rating",
    [
        (BookStatus.PLANNED, None),
        (BookStatus.READING, None),
        (BookStatus.READ, 5),
        (BookStatus.ABANDONED, None),
        (None, 5),
        (None, None),
    ],
)
def test_shelf_entry_update_check_rating_correct(status, rating):
    shelf_entry_update = ShelfEntryUpdate(status=status, rating=rating)
    assert shelf_entry_update.status == status and shelf_entry_update.rating is rating


@pytest.mark.parametrize(
    "status,rating",
    [
        (BookStatus.PLANNED, 5),
        (BookStatus.READING, 5),
        (BookStatus.ABANDONED, 5),
    ],
)
def test_shelf_entry_update_check_rating_incorrect(status, rating):
    with pytest.raises(ValueError):
        ShelfEntryUpdate(status=status, rating=rating)
