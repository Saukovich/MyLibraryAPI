import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.database import SessionDep
from app.core.security import decode_access_token
from app.models.users import User
from app.repositories.user_repository import UserRepository


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")


async def get_current_user(session: SessionDep, token: str = Depends(oauth2_scheme)) -> User:
    """
    Получение текущего пользователя из токена JWT.
    Args:
        session: SessionDep -- сессия базы данных.
        token: str -- токен JWT.

    Returns:
        User -- текущий пользователь.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )  # Исключение для невалидных токенов
    try:
        user_id = decode_access_token(token)  # Декодирование токена
    except jwt.PyJWTError:
        raise credentials_exception

    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(id=user_id)
    if user is None:  # Проверка существования пользователя
        raise credentials_exception
    return user
