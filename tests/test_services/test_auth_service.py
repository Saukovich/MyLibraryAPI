import pytest
from fastapi import HTTPException

from app.core.security import decode_access_token
from app.repositories.user_repository import UserRepository
from app.schemas.user_schemas import UserLoginRequest, UserRegisterRequest
from app.services.auth_service import AuthService


@pytest.fixture
def auth_service(db_session):
    """Фикстура для создания экземпляра AuthService."""
    user_repository = UserRepository(db_session)
    return AuthService(user_repository)


@pytest.mark.asyncio
async def test_auth_service_register_happy_path(auth_service):
    """Тестирование регистрации нового пользователя."""
    user_register_request = UserRegisterRequest(username="test", email="test@test.com", password="testtest")
    user = await auth_service.register(user_register_request)
    assert (
        user is not None
        and user.username == user_register_request.username
        and user.email == user_register_request.email
    )


@pytest.mark.asyncio
async def test_auth_service_register_existing_user_by_username_raises_409(auth_service):
    """Тестирование регистрации существующего пользователя по username."""
    user_register_request = UserRegisterRequest(username="test", email="test@test.com", password="testtest")
    await auth_service.register(user_register_request)

    # Попытка зарегистрировать пользователя с существующим username
    user_register_request = UserRegisterRequest(username="test", email="test1@test.com", password="testtest")
    with pytest.raises(HTTPException) as exc_info:
        await auth_service.register(user_register_request)
    assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_auth_service_register_existing_user_by_email_raises_409(auth_service):
    """Тестирование регистрации существующего пользователя по email."""
    user_register_request = UserRegisterRequest(username="test", email="test@test.com", password="testtest")
    await auth_service.register(user_register_request)

    # Попытка зарегистрировать пользователя с существующим email
    user_register_request = UserRegisterRequest(username="test1", email="test@test.com", password="testtest")
    with pytest.raises(HTTPException) as exc_info:
        await auth_service.register(user_register_request)
    assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_auth_service_login_happy_path(auth_service):
    """Тестирование логина пользователя."""
    user_register_request = UserRegisterRequest(username="test", email="test@test.com", password="testtest")
    user = await auth_service.register(user_register_request)

    user_login_request = UserLoginRequest(username="test", password="testtest")
    token = await auth_service.login(user_login_request)
    user_id = decode_access_token(token)

    assert user.id == user_id


@pytest.mark.asyncio
async def test_auth_service_login_invalid_credentials_raises_401(auth_service):
    """Тестирование логина с неверными учетными данными."""
    user_login_request = UserLoginRequest(username="test", password="testtest")
    # Пользователь не существует, поэтому должно быть выброшено исключение 401
    with pytest.raises(HTTPException) as exc_info:
        await auth_service.login(user_login_request)

    assert exc_info.value.status_code == 401

    user_register_request = UserRegisterRequest(username="test", email="test@test.com", password="testtest")
    await auth_service.register(user_register_request)

    user_login_request = UserLoginRequest(username="test", password="testtest1")
    # Неверный пароль, поэтому должно быть выброшено исключение 401
    with pytest.raises(HTTPException) as exc_info:
        await auth_service.login(user_login_request)

    assert exc_info.value.status_code == 401


async def test_auth_service_get_me_happy_path(auth_service):
    """Тестирование получения информации о пользователе."""
    user_register_request = UserRegisterRequest(username="test", email="test@test.com", password="testtest")
    user = await auth_service.register(user_register_request)

    got_user = await auth_service.get_me(user.id)
    assert got_user.id == user.id and got_user.username == user.username and got_user.email == user.email


async def test_auth_service_get_me_user_not_exist_raises_404(auth_service):
    """Тестирование получения информации о несуществующем пользователе."""
    # Пользователь не существует, поэтому должно быть выброшено исключение 404
    with pytest.raises(HTTPException) as exc_info:
        await auth_service.get_me(1)
    assert exc_info.value.status_code == 404
