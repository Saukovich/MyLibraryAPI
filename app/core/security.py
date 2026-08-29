from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from app.core.config import load_config


config = load_config()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Хэширует пароль перед сохранением в БД."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Сравнивает введенный пароль с хэшированным паролем из БД."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int) -> str:
    """
    Создает JWT токен для аутентификации пользователя.
    Args:
        user_id: int -- ID пользователя

    Returns:
        str -- JWT токен
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=config.access_token_expire_minutes)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, config.secret_key, algorithm=config.algorithm)


def decode_access_token(token: str) -> int:
    """
    Декодирует JWT токен и возвращает ID пользователя.
    Args:
        token: str -- JWT токен.

    Returns:
        int -- ID пользователя.
    """
    payload = jwt.decode(token, config.secret_key, algorithms=[config.algorithm])
    return int(payload["sub"])
