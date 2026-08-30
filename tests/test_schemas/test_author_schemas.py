import pytest
from pydantic import TypeAdapter

from app.schemas.author_schemas import AuthorBase, AuthorRef, AuthorUpdate, ExistingAuthorRef, NewAuthorRef


@pytest.mark.parametrize(
    "birth_year,death_year",
    [
        (1900, 2000),
        (1900, None),
    ],
)
def test_author_schemas_author_base_validate_years_correct(birth_year, death_year):
    """Тест с корректными годами рождения и смерти автора."""
    author_base = AuthorBase(fullname="Test Author", birth_year=birth_year, death_year=death_year)
    assert author_base.birth_year == birth_year and author_base.death_year is death_year


def test_author_schemas_author_base_validate_years_incorrect():
    """Тест с некорректными годами рождения и смерти автора."""
    with pytest.raises(ValueError):
        AuthorBase(fullname="Test Author", birth_year=2000, death_year=1900)


def test_author_update_partial_does_not_catch_cross_field_inconsistency():
    """Ограничение: AuthorUpdate валидирует только переданные поля,
    не текущее состояние записи в БД. Эта проверка - ответсвтенность сервиса."""
    author_update = AuthorUpdate(birth_year=1900)
    assert author_update.death_year is None


def test_author_schemas_author_ref_resolves_existing():
    """Тест, что ExistingAuthorRef создается правильно."""
    author_ref = TypeAdapter(AuthorRef).validate_python({"id": 1})
    assert isinstance(author_ref, ExistingAuthorRef)


def test_author_schemas_author_ref_resolves_new():
    """Тест, что NewAuthorRef создается правильно."""
    author_ref = TypeAdapter(AuthorRef).validate_python({"fullname": "Test Author", "birth_year": 1900})
    assert isinstance(author_ref, NewAuthorRef)
