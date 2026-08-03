import pytest

from app.schemas.params import AuthorFilterParams, BookFilterParams, PaginationParams


@pytest.mark.parametrize("limit,offset", [(0, 0), (-1, -1), (101, 0), (100, -1)])
def test_pagination_params_raises_value_error(limit, offset):
    """Тест для проверки параметров пагинации."""
    with pytest.raises(ValueError):
        PaginationParams(limit=limit, offset=offset)


@pytest.mark.parametrize("author_name", ["", "A" * 256])
def test_book_filter_params_author_name_raises_value_error(author_name):
    """Тест для проверки имени автора."""
    with pytest.raises(ValueError):
        BookFilterParams(author_name=author_name)


@pytest.mark.parametrize("release_year_min,release_year_max", [(2000, 1999), (-1999, 1), (-1, -1), (0, 0)])
def test_book_filter_params_release_year_raises_value_error(release_year_min, release_year_max):
    """Тест для проверки года выпуска книги."""
    with pytest.raises(ValueError):
        BookFilterParams(release_year_min=release_year_min, release_year_max=release_year_max)


@pytest.mark.parametrize("fullname", ["", "A" * 256])
def test_author_filter_params_fullname_raises_value_error(fullname):
    """Тест для проверки полного имени автора."""
    with pytest.raises(ValueError):
        AuthorFilterParams(fullname=fullname)


@pytest.mark.parametrize("birth_year_min,birth_year_max", [(2000, 1999), (-1999, 1), (-1, -1), (0, 0)])
def test_author_filter_params_birth_year_raises_value_error(birth_year_min, birth_year_max):
    """Тест для проверки годов рождения автора."""
    with pytest.raises(ValueError):
        AuthorFilterParams(birth_year_min=birth_year_min, birth_year_max=birth_year_max)


@pytest.mark.parametrize("death_year_min,death_year_max", [(2000, 1999), (-1999, 1), (-1, -1), (0, 0)])
def test_author_filter_params_death_year_raises_value_error(death_year_min, death_year_max):
    """Тест для проверки годов смерти автора."""
    with pytest.raises(ValueError):
        AuthorFilterParams(death_year_min=death_year_min, death_year_max=death_year_max)


@pytest.mark.parametrize("death_year_min,death_year_max", [(1999, None), (None, 1999), (1999, 1999)])
def test_author_filter_params_is_dead_raises_value_error(death_year_min, death_year_max):
    """Тест для проверки статуса жизни автора."""
    with pytest.raises(ValueError):
        AuthorFilterParams(is_dead=False, death_year_min=death_year_min, death_year_max=death_year_max)


@pytest.mark.parametrize(
    "birth_year_min,birth_year_max,death_year_min,death_year_max",
    [
        (1800, None, 1790, None),
        (1800, None, None, 1790),
        (1800, None, 1790, 1800),
        (None, 1800, None, 1790),
        (1800, 1800, 1790, 1790),
        (1800, 1800, 1790, 1800),
    ],
)
def test_author_filter_params_combination_years_raises_value_error(
    birth_year_min, birth_year_max, death_year_min, death_year_max
):
    """Тест для проверки комбинаций годов рождения и смерти."""
    with pytest.raises(ValueError):
        AuthorFilterParams(
            birth_year_min=birth_year_min,
            birth_year_max=birth_year_max,
            death_year_min=death_year_min,
            death_year_max=death_year_max,
        )
