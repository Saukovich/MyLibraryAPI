import pytest


@pytest.mark.asyncio
async def test_auth_router_login_happy_path(client, existing_user):
    """Тестирование успешного входа в систему."""
    response = await client.post("api/v1/login", json={"username": existing_user.username, "password": "testtest"})
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_auth_router_login_wrong_password(client, existing_user):
    """Тестирование входа с неправильным паролем."""
    response = await client.post("api/v1/login", json={"username": existing_user.username, "password": "wrongpassword"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_auth_router_login_nonexistent_user(client):
    """Тестирование входа с несуществующим пользователем."""
    response = await client.post("api/v1/login", json={"username": "nonexistentuser", "password": "testtest"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_auth_router_register_happy_path(client):
    """Тестирование успешной регистрации нового пользователя."""
    response = await client.post(
        "api/v1/register", json={"username": "newuser", "email": "newuser@example.com", "password": "testtest"}
    )
    assert response.status_code == 201
    assert response.json()["username"] == "newuser"
    assert response.json()["email"] == "newuser@example.com"


@pytest.mark.asyncio
async def test_auth_router_register_existing_user(client, existing_user):
    """Тестирование попытки зарегистрировать существующего пользователя."""
    response = await client.post(
        "api/v1/register",
        json={"username": existing_user.username, "email": "newuser@example.com", "password": "testtest"},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_auth_router_get_me(authenticated_client, existing_user):
    """Тестирование получения информации о пользователе."""
    response = await authenticated_client.get("api/v1/users/me")
    assert response.status_code == 200
    assert response.json()["username"] == existing_user.username
    assert response.json()["email"] == existing_user.email


@pytest.mark.asyncio
async def test_auth_router_get_me_unauthorized(client):
    """Тестирование попытки получить информацию о пользователе без авторизации."""
    response = await client.get("api/v1/users/me")
    assert response.status_code == 401
