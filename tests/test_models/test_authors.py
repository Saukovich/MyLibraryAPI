import pytest

from app.models.authors import Author


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "author",
    [
        {"fullname": "Lev Nikolayevich Tolstoy", "birth_year": 1828, "death_year": 1910},
        {"fullname": "Alexandes Sergeyevich Pushkin", "birth_year": 1799, "death_year": 1837},
        {"fullname": "Fyodor Mikhailovich Dostoyevsky", "birth_year": 1821, "death_year": 1881},
        {"fullname": "Anton Pavlovich Chekhov", "birth_year": 1860, "death_year": 1904},
        {"fullname": "Viktor Olegovich Pelevin", "birth_year": 1962, "death_year": None},
        {"fullname": "V" * 100, "birth_year": 2000, "death_year": None},
    ],
)
async def test_authors_with_correct_data(author, db_session):
    """Тест на создание автора с корректными данными."""
    author = Author(**author)
    db_session.add(author)

    await db_session.commit()
    await db_session.refresh(author)

    assert author.id is not None
    assert author.created_at is not None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "author",
    [
        {"fullname": None, "birth_year": 1828, "death_year": 1910},
        {"fullname": "Alexandes Sergeyevich Pushkin", "birth_year": None, "death_year": 1837},
        {"fullname": None, "birth_year": None, "death_year": 1881},
    ],
)
async def test_insert_author_with_null_fullname_or_birth_year_raises_value_error(author, db_session):
    """Тест на создание автора с пустым полем fullname или birth_year."""
    with pytest.raises(ValueError):
        db_session.add(Author(**author))
        await db_session.commit()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "author",
    [
        {"fullname": "L" * 105, "birth_year": 1828, "death_year": 1910},
        {"fullname": "A" * 1000, "birth_year": 1799, "death_year": 1837},
        {"fullname": "F" * 125, "birth_year": 1821, "death_year": 1881},
        {"fullname": "A" * 1204, "birth_year": 1860, "death_year": 1904},
        {"fullname": "V" * 101, "birth_year": 1962, "death_year": None},
    ],
)
async def test_insert_author_where_fullname_exceeds_max_length_raises_value_error(author, db_session):
    """Тест на создание автора с полем fullname длиннее 100 символов."""
    with pytest.raises(ValueError):
        db_session.add(Author(**author))
        await db_session.commit()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "author",
    [
        {"fullname": "Lev Nikolayevich Tolstoy", "birth_year": -1, "death_year": 1910},
        {"fullname": "Alexandes Sergeyevich Pushkin", "birth_year": 0, "death_year": 1837},
        {"fullname": "Fyodor Mikhailovich Dostoyevsky", "birth_year": -1000, "death_year": 1881},
        {"fullname": "Anton Pavlovich Chekhov", "birth_year": -124531, "death_year": 1904},
        {"fullname": "Viktor Olegovich Pelevin", "birth_year": -21312332, "death_year": None},
        {"fullname": "V" * 100, "birth_year": -131234, "death_year": None},
    ],
)
async def test_insert_author_with_negative_birth_year_raises_value_error(author, db_session):
    """Тест на создание автора с отрицательным годом рождения."""
    with pytest.raises(ValueError):
        db_session.add(Author(**author))
        await db_session.commit()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "author",
    [
        {"fullname": "Lev Nikolayevich Tolstoy", "birth_year": 1828, "death_year": 0},
        {"fullname": "Alexandes Sergeyevich Pushkin", "birth_year": 1799, "death_year": -1},
        {"fullname": "Fyodor Mikhailovich Dostoyevsky", "birth_year": 1821, "death_year": -123123213},
        {"fullname": "Anton Pavlovich Chekhov", "birth_year": 1860, "death_year": -13},
        {"fullname": "Viktor Olegovich Pelevin", "birth_year": 1962, "death_year": -1239},
        {"fullname": "V" * 100, "birth_year": 2000, "death_year": -7},
    ],
)
async def test_insert_author_with_negative_death_year_raises_value_error(author, db_session):
    """Тест на создание автора с отрицательным годом смерти."""
    with pytest.raises(ValueError):
        db_session.add(Author(**author))
        await db_session.commit()
