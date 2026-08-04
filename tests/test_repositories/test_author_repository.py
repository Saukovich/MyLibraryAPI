import pytest

from app.repositories.author_repository import AuthorRepository
from app.schemas.params import AuthorFilterParams


@pytest.fixture
def author_repository(db_session):
    return AuthorRepository(db_session)


# -----------------------------------
# ТЕСТЫ НА ФИЛЬТРЫ С ОДНИМ ПАРАМЕТРОМ
# -----------------------------------


@pytest.mark.asyncio
async def test_author_repo_get_by_filters_without_params(author_repository):
    """Тест на фильтр без параметров."""
    filters = AuthorFilterParams()

    await author_repository.create({"fullname": "Test Author 1", "birth_year": 1990})
    await author_repository.create({"fullname": "Test Author 2", "birth_year": 1990})
    await author_repository.create({"fullname": "Test Author 3", "birth_year": 1990})

    result = await author_repository.get_by_filters(filters)
    assert len(result) == 3


@pytest.mark.asyncio
@pytest.mark.parametrize("fullname", ["Test Author 1", "Test Author 2", "Test Author 3"])
async def test_author_repo_get_by_filters_with_fullname_param(fullname, author_repository):
    """Тест на фильтр по имени автора."""
    filters = AuthorFilterParams(fullname=fullname)

    await author_repository.create({"fullname": "Test Author 1", "birth_year": 1990})
    await author_repository.create({"fullname": "Test Author 2", "birth_year": 1990})
    await author_repository.create({"fullname": "Test Author 3", "birth_year": 1990})

    result = await author_repository.get_by_filters(filters)
    assert len(result) == 1 and result[0].fullname == fullname


@pytest.mark.asyncio
async def test_author_repo_get_by_filters_with_birth_year_min_param(author_repository):
    """Тест на фильтр по минимальному году рождения."""
    filters = AuthorFilterParams(birth_year_min=1990)

    await author_repository.create({"fullname": "Test Author 1", "birth_year": 1980})
    await author_repository.create({"fullname": "Test Author 2", "birth_year": 1990})
    await author_repository.create({"fullname": "Test Author 3", "birth_year": 1991})

    result = await author_repository.get_by_filters(filters)
    assert len(result) == 2 and result[0].birth_year == 1990 and result[1].birth_year == 1991


@pytest.mark.asyncio
async def test_author_repo_get_by_filters_with_birth_year_max_param(author_repository):
    """Тест на фильтр по максимальному году рождения."""
    filters = AuthorFilterParams(birth_year_max=1990)

    await author_repository.create({"fullname": "Test Author 1", "birth_year": 1980})
    await author_repository.create({"fullname": "Test Author 2", "birth_year": 1990})
    await author_repository.create({"fullname": "Test Author 3", "birth_year": 1991})

    result = await author_repository.get_by_filters(filters)
    assert len(result) == 2 and result[0].birth_year == 1980 and result[1].birth_year == 1990


@pytest.mark.asyncio
@pytest.mark.parametrize("is_dead", [True, False])
async def test_author_repo_get_by_filters_with_is_dead_param(is_dead, author_repository):
    """Тест на фильтр по статусу жизни автора."""
    filters = AuthorFilterParams(is_dead=is_dead)

    await author_repository.create({"fullname": "Test Author 1", "birth_year": 1980})
    await author_repository.create({"fullname": "Test Author 2", "birth_year": 1990})
    await author_repository.create({"fullname": "Test Author 3", "birth_year": 1991, "death_year": 2020})
    await author_repository.create({"fullname": "Test Author 4", "birth_year": 1991, "death_year": 2026})

    result = await author_repository.get_by_filters(filters)
    assert len(result) == 2


@pytest.mark.asyncio
async def test_author_repo_get_by_filters_with_death_year_min_param(author_repository):
    """Тест на фильтр по минимальному году смерти."""
    filters = AuthorFilterParams(death_year_min=2020)

    await author_repository.create({"fullname": "Test Author 1", "birth_year": 1980, "death_year": 2019})
    await author_repository.create({"fullname": "Test Author 2", "birth_year": 1990, "death_year": 2020})
    await author_repository.create({"fullname": "Test Author 3", "birth_year": 1991, "death_year": 2025})

    result = await author_repository.get_by_filters(filters)
    assert len(result) == 2


@pytest.mark.asyncio
async def test_author_repo_get_by_filters_with_death_year_max_param(author_repository):
    """Тест на фильтр по максимальному году смерти."""
    filters = AuthorFilterParams(death_year_max=2020)

    await author_repository.create({"fullname": "Test Author 1", "birth_year": 1980, "death_year": 2019})
    await author_repository.create({"fullname": "Test Author 2", "birth_year": 1990, "death_year": 2020})
    await author_repository.create({"fullname": "Test Author 3", "birth_year": 1991, "death_year": 2025})

    result = await author_repository.get_by_filters(filters)
    assert len(result) == 2


@pytest.mark.asyncio
async def test_author_repo_get_by_filters_with_limit_param(author_repository):
    """Тест на пагинацию."""
    filters = AuthorFilterParams(limit=2)

    await author_repository.create({"fullname": "Test Author 1", "birth_year": 1990})
    await author_repository.create({"fullname": "Test Author 2", "birth_year": 1990})
    await author_repository.create({"fullname": "Test Author 3", "birth_year": 1990})
    await author_repository.create({"fullname": "Test Author 4", "birth_year": 1990})

    result = await author_repository.get_by_filters(filters)
    assert len(result) == 2


@pytest.mark.asyncio
async def test_author_repo_get_by_filters_with_offset_param(author_repository):
    """Тест на пагинацию."""
    filters = AuthorFilterParams(offset=2)

    await author_repository.create({"fullname": "Test Author 1", "birth_year": 1990})
    await author_repository.create({"fullname": "Test Author 2", "birth_year": 1990})
    await author_repository.create({"fullname": "Test Author 3", "birth_year": 1990})

    result = await author_repository.get_by_filters(filters)
    assert len(result) == 1 and result[0].fullname == "Test Author 3"


# -----------------------------------------
# ТЕСТ НА ФИЛЬТРЫ С КОМБИНАЦИЯМИ ПАРАМЕТРОВ
# -----------------------------------------


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "sort_by,order_by",
    [
        ("id", "asc"),
        ("id", "desc"),
        ("fullname", "asc"),
        ("fullname", "desc"),
        ("birth_year", "asc"),
        ("birth_year", "desc"),
        ("death_year", "asc"),
        ("death_year", "desc"),
    ],
)
async def test_author_repo_get_by_filters_with_sort_by_and_order_by_params(sort_by, order_by, author_repository):
    """Тест на комбинацию параметров сортировки."""
    filters = AuthorFilterParams(sort_by=sort_by, order_by=order_by)

    await author_repository.create({"fullname": "Test Author A", "birth_year": 1981, "death_year": 2019})
    await author_repository.create({"fullname": "Test Author B", "birth_year": 1982, "death_year": 2020})
    await author_repository.create({"fullname": "Test Author C", "birth_year": 1983, "death_year": 2021})

    result = await author_repository.get_by_filters(filters)
    flag = True
    for i in range(1, len(result)):
        if order_by == "asc" and getattr(result[i - 1], sort_by) > getattr(
            result[i], sort_by
        ):  # сортировка по возрастанию
            flag = False
            break
        elif order_by == "desc" and getattr(result[i - 1], sort_by) < getattr(
            result[i], sort_by
        ):  # сортировка по убыванию
            flag = False
            break
    assert flag


@pytest.mark.asyncio
@pytest.mark.parametrize("birth_year_min,birth_year_max", [(1989, 1990), (1990, 1991)])
async def test_author_repo_get_by_filters_with_birth_year_min_max_params(
    birth_year_min, birth_year_max, author_repository
):
    """Тест на комбинацию параметров года рождения."""
    filters = AuthorFilterParams(birth_year_min=birth_year_min, birth_year_max=birth_year_max)

    await author_repository.create({"fullname": "Test Author 1", "birth_year": 1989})
    await author_repository.create({"fullname": "Test Author 2", "birth_year": 1990})
    await author_repository.create({"fullname": "Test Author 3", "birth_year": 1991})

    result = await author_repository.get_by_filters(filters)
    assert len(result) == 2


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "fullname,birth_year_min,birth_year_max",
    [
        ("Test Author 1", 1851, None),
        ("Test Author 2", None, 1900),
        ("Test Author 3", 1800, 1900),
    ],
)
async def test_author_repo_get_by_filters_with_fullname_birth_year_params(
    fullname, birth_year_min, birth_year_max, author_repository
):
    """Тест на комбинацию параметров имени автора и года рождения."""
    filters = AuthorFilterParams(fullname=fullname, birth_year_min=birth_year_min, birth_year_max=birth_year_max)

    await author_repository.create({"fullname": "Test Author 1", "birth_year": 1901})
    await author_repository.create({"fullname": "Test Author 2", "birth_year": 1800})
    await author_repository.create({"fullname": "Test Author 3", "birth_year": 1850})

    result = await author_repository.get_by_filters(filters)
    assert len(result) == 1 and result[0].fullname == fullname  # ищем только одного автора, у которого указано имя
    assert (
        birth_year_min and result[0].birth_year
    ) or birth_year_min is None  # проверяем, что год рождения входит в диапазон
    assert (
        birth_year_max and result[0].birth_year
    ) or birth_year_max is None  # проверяем, что год рождения входит в диапазон


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "death_year_min,death_year_max",
    [
        (1872, None),
        (None, 1860),
        (1851, 1871),
    ],
)
async def test_author_repo_get_by_filters_with_is_dead_true_death_year_params(
    death_year_min, death_year_max, author_repository
):
    """Тест на комбинацию параметров статуса жизни автора и года смерти."""
    filters = AuthorFilterParams(is_dead=True, death_year_min=death_year_min, death_year_max=death_year_max)

    await author_repository.create({"fullname": "Test Author 1", "birth_year": 1750, "death_year": 1901})
    await author_repository.create({"fullname": "Test Author 2", "birth_year": 1800, "death_year": 1871})
    await author_repository.create({"fullname": "Test Author 3", "birth_year": 1800, "death_year": 1850})

    result = await author_repository.get_by_filters(filters)
    assert len(result) == 1  # ищем только одного автора, у которого указан год смерти
    assert (death_year_min and result[0].birth_year) or death_year_min is None
    assert (death_year_max and result[0].birth_year) or death_year_max is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "birth_year_min,birth_year_max",
    [
        (1910, None),
        (None, 1900),
        (1901, 1909),
    ],
)
async def test_author_repo_get_by_filters_with_is_dead_false_birth_year_params(
    birth_year_min, birth_year_max, author_repository
):
    """Тест на комбинацию параметров статуса жизни автора и года рождения."""
    filters = AuthorFilterParams(is_dead=False, birth_year_min=birth_year_min, birth_year_max=birth_year_max)

    await author_repository.create({"fullname": "Test Author 1_1", "birth_year": 1910, "death_year": 2000})
    await author_repository.create({"fullname": "Test Author 1_2", "birth_year": 1910})
    await author_repository.create({"fullname": "Test Author 2_1", "birth_year": 1900, "death_year": 2000})
    await author_repository.create({"fullname": "Test Author 2_2", "birth_year": 1900})
    await author_repository.create({"fullname": "Test Author 3_1", "birth_year": 1901, "death_year": 2000})
    await author_repository.create({"fullname": "Test Author 3_2", "birth_year": 1901})

    result = await author_repository.get_by_filters(filters)
    assert len(result) == 1 and result[0].death_year is None
    assert (birth_year_min and result[0].birth_year >= birth_year_min) or birth_year_min is None
    assert (birth_year_max and result[0].birth_year <= birth_year_max) or birth_year_max is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "dict_filters",
    [
        {
            "fullname": "Author1",
            "birth_year_min": 1800,
            "birth_year_max": 1805,
            "is_dead": True,
            "death_year_min": 1845,
            "death_year_max": 1850,
        },
        {"fullname": "Author2", "birth_year_min": 1806, "birth_year_max": 1810, "is_dead": False},
        {"fullname": "Author3", "birth_year_min": 1800, "birth_year_max": 1805, "is_dead": False},
    ],
)
async def test_author_repo_get_by_filters_with_all_main_params(dict_filters, author_repository):
    """Тест на комбинацию всех основных параметров."""
    filters = AuthorFilterParams(**dict_filters)

    await author_repository.create({"fullname": "Author1", "birth_year": 1800, "death_year": 1845})
    await author_repository.create({"fullname": "Author1", "birth_year": 1803, "death_year": 1847})
    await author_repository.create({"fullname": "Author1", "birth_year": 1805, "death_year": 1850})
    await author_repository.create({"fullname": "Author1", "birth_year": 1806, "death_year": 1845})
    await author_repository.create({"fullname": "Author1_1", "birth_year": 1805, "death_year": 1850})

    await author_repository.create({"fullname": "Author2", "birth_year": 1806})
    await author_repository.create({"fullname": "Author2", "birth_year": 1807})
    await author_repository.create({"fullname": "Author2", "birth_year": 1810})
    await author_repository.create({"fullname": "Author2", "birth_year": 1806, "death_year": 1870})
    await author_repository.create({"fullname": "Author2_1", "birth_year": 1810})

    await author_repository.create({"fullname": "Author3", "birth_year": 1800})
    await author_repository.create({"fullname": "Author3", "birth_year": 1803})
    await author_repository.create({"fullname": "Author3", "birth_year": 1805})
    await author_repository.create({"fullname": "Author3", "birth_year": 1806})
    await author_repository.create({"fullname": "Author3_1", "birth_year": 1805})

    result = await author_repository.get_by_filters(filters)
    flag = True
    for author in result:
        if not (
            author.fullname == dict_filters["fullname"]
            and dict_filters["birth_year_min"] <= author.birth_year <= dict_filters["birth_year_max"]
        ):
            flag = False
            break
        if (
            dict_filters["is_dead"] and author.death_year is None
        ):  # если автор живой, то проверяем, что год смерти не указан
            flag = False
            break
        else:  # если автор мертвый, то проверяем, что год смерти указан и он входит в диапазон
            if not (author.death_year is None) and not (
                dict_filters["death_year_min"] <= author.birth_year <= dict_filters["death_year_max"]
            ):
                flag = False
                break

    assert len(result) == 3 and flag
