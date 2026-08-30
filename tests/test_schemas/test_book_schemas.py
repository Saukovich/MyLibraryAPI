from types import SimpleNamespace

from app.schemas.book_schemas import BookResponse, PopularBookResponse


def test_book_schemas_book_response_validate_authors():
    """Тестируем валидацию списка авторов."""
    fake_authors = [
        SimpleNamespace(fullname="Толстой Лев Николаевич"),
        SimpleNamespace(fullname="Достоевский Федор Михайлович"),
    ]

    book_response = BookResponse(id=1, title="Тест", release_year=2023, authors=fake_authors)

    assert book_response.authors == ["Толстой Лев Николаевич", "Достоевский Федор Михайлович"]


def test_book_schemas_book_response_empty_authors():
    """Тестируем валидацию пустого списка авторов."""
    book_response = BookResponse(id=1, title="Тест", release_year=2023, authors=[])
    assert book_response.authors == []


def test_book_schemas_popular_book_response_flatten_dto():
    """Тестируем валидацию PopularBookResponse."""
    fake_book = SimpleNamespace(id=1, title="Тест", release_year=2023, authors=[SimpleNamespace(fullname="Автор")])
    fake_row = SimpleNamespace(book=fake_book, number_of_additions=10, avg_rating=4.5)
    response = PopularBookResponse.model_validate(fake_row)

    assert response.id == 1
    assert response.title == "Тест"
    assert response.release_year == 2023
    assert response.authors == ["Автор"]
    assert response.number_of_additions == 10
    assert response.avg_rating == 4.5


def test_book_schemas_popular_book_response_avg_rating_none():
    """Тестируем валидацию PopularBookResponse с avg_rating=None."""
    fake_book = SimpleNamespace(id=1, title="Тест", release_year=2023, authors=[SimpleNamespace(fullname="Автор")])
    fake_row = SimpleNamespace(book=fake_book, number_of_additions=10, avg_rating=None)
    response = PopularBookResponse.model_validate(fake_row)
    assert response.avg_rating is None
