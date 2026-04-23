import pytest

from app.models.users import User


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user",
    [
        {"username": "test_user", "email": "test@gmail.com", "password": "test"},
        {"username": "fivec", "email": "test@gmail.com", "password": "t" * 255},
        {"username": "t" * 50, "email": "test@gmail.com", "password": "test"},
    ],
)
async def test_user_with_correct_data(user, db_session):
    """Тестирование добавления пользователя с корректными данными"""
    user = User(**user)
    db_session.add(user)

    await db_session.commit()
    await db_session.refresh(user)

    assert user.id is not None
    assert user.created_at is not None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user",
    [
        {"username": None, "email": "test@gmail.com", "password": "test"},
        {"username": "test_user", "email": None, "password": "test"},
        {"username": "test_user", "email": "test@gmail.com", "password": None},
        {"username": "test_user", "email": "test@gmail.com", "password": ""},
        {"username": None, "email": None, "password": None},
    ],
)
async def test_insert_user_with_null_fields_raises_value_error(user, db_session):
    """Тестирование добавления пользователя с пустыми полями"""
    with pytest.raises(ValueError):
        db_session.add(User(**user))
        await db_session.commit()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user",
    [
        {"username": "tttt", "email": "test@gmail.com", "password": "test"},
        {"username": "ttt", "email": "test@gmail.com", "password": "test"},
        {"username": "tt", "email": "test@gmail.com", "password": "test"},
        {"username": "t", "email": "test@gmail.com", "password": "test"},
        {"username": "", "email": "test@gmail.com", "password": "test"},
    ],
)
async def test_insert_user_where_username_is_too_short_raises_value_error(user, db_session):
    """Тестирование добавления пользователя с коротким username"""
    with pytest.raises(ValueError):
        db_session.add(User(**user))
        await db_session.commit()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user",
    [
        {"username": "t" * 51, "email": "test@gmail.com", "password": "test"},
        {"username": "t" * 256, "email": "test@gmail.com", "password": "test"},
        {"username": "t" * 500, "email": "test@gmail.com", "password": "test"},
        {"username": "t" * 1000, "email": "test@gmail.com", "password": "test"},
    ],
)
async def test_insert_user_where_username_exceeds_max_length_raises_value_error(user, db_session):
    """Тестирование добавления пользователя с длинным username"""
    with pytest.raises(ValueError):
        db_session.add(User(**user))
        await db_session.commit()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user",
    [
        {"username": "test_user", "email": "test", "password": "test"},
        {"username": "test_user", "email": "test@", "password": "test"},
        {"username": "test_user", "email": "test@gmail", "password": "test"},
        {"username": "test_user", "email": "test@gmail.", "password": "test"},
        {"username": "test_user", "email": "", "password": "test"},
        {"username": "test_user", "email": "@gmail.com", "password": "test"},
        {"username": "test_user", "email": "@gmail.", "password": "test"},
        {"username": "test_user", "email": "gmail.com", "password": "test"},
        {"username": "test_user", "email": "gmail.", "password": "test"},
        {"username": "test_user", "email": "gmail.com@test", "password": "test"},
        {"username": "test_user", "email": "gmail.com@test.", "password": "test"},
    ],
)
async def test_insert_user_where_email_is_invalid_raises_value_error(user, db_session):
    """Тестирование добавления пользователя с некорректным email"""
    with pytest.raises(ValueError):
        db_session.add(User(**user))
        await db_session.commit()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user",
    [
        {"username": "test_user", "email": "t" * 100 + "@gmail.com", "password": "test"},
        {"username": "test_user", "email": "t" * 255 + "@gmail.com", "password": "test"},
        {"username": "test_user", "email": "t" * 1000 + "@gmail.com", "password": "test"},
    ],
)
async def test_insert_user_where_email_exceeds_max_length_raises_value_error(user, db_session):
    """Тестирование добавления пользователя с длинным email"""
    with pytest.raises(ValueError):
        db_session.add(User(**user))
        await db_session.commit()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user",
    [
        {"username": "test_user", "email": "test@gmail.com", "password": "t" * 256},
        {"username": "test_user", "email": "test@gmail.com", "password": "t" * 1000},
        {"username": "test_user", "email": "test@gmail.com", "password": "t" * 10000},
    ],
)
async def test_insert_user_where_password_exceeds_max_length_raises_value_error(user, db_session):
    """Тестирование добавления пользователя с длинным password"""
    with pytest.raises(ValueError):
        db_session.add(User(**user))
        await db_session.commit()
