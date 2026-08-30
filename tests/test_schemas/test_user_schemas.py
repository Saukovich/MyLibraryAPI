import pytest

from app.schemas.user_schemas import UserLoginRequest


@pytest.mark.parametrize("username,email", [("test", "test@test.com"), ("test", None), (None, "test@test.com")])
def test_user_login_request_username_email_correct(username, email):
    """Тест на то, что при передаче username или email в UserLoginRequest происходит корректное создание объекта."""
    user_login_request = UserLoginRequest(username=username, email=email, password="testtest")
    assert user_login_request.username is username or user_login_request.email is email


def test_user_login_request_username_email_incorrect():
    """Тест на то, что при передаче одновременно username и email в UserLoginRequest происходит исключение."""
    with pytest.raises(ValueError):
        UserLoginRequest(username=None, email=None, password="testtest")
