import pytest

from app.repositories.user_repository import UserRepository


@pytest.fixture
def user_repository(db_session):
    """Фикстура для создания экземпляра UserRepository."""
    return UserRepository(db_session)


@pytest.mark.asyncio
async def test_user_repo_get_user_by_username(user_repository):
    """Тест для проверки получения пользователя по username."""
    await user_repository.create(
        {"username": "testuser", "email": "testuser@gmail.com", "password_hash": "testpassword"}
    )
    user = await user_repository.get_user_by_username("testuser")
    assert user.username == "testuser"


@pytest.mark.asyncio
async def test_user_repo_get_user_by_email(user_repository):
    """Тест для проверки получения пользователя по email."""
    await user_repository.create(
        {"username": "testuser", "email": "testuser@gmail.com", "password_hash": "testpassword"}
    )
    user = await user_repository.get_user_by_email("testuser@gmail.com")
    assert user.email == "testuser@gmail.com"


@pytest.mark.asyncio
async def test_user_repo_exists_user_by_username(user_repository):
    """Тест для проверки существования пользователя по username."""
    await user_repository.create(
        {"username": "testuser", "email": "testuser@gmail.com", "password_hash": "testpassword"}
    )
    exists = await user_repository.exists_user_by_username("testuser")
    assert exists


@pytest.mark.asyncio
async def test_user_repo_exists_user_by_email(user_repository):
    """Тест для проверки существования пользователя по email."""
    await user_repository.create(
        {"username": "testuser", "email": "testuser@gmail.com", "password_hash": "testpassword"}
    )
    exists = await user_repository.exists_user_by_email("testuser@gmail.com")
    assert exists
