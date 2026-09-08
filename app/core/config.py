import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass
class DatabaseConfig:
    """
    Настройки базы данных.

    Attributes:
        database_url: str - URL подключения к базе данных
    """

    database_url: str


@dataclass
class Config:
    """
    Конфигурация приложения.

    Attributes:
        db: DatabaseConfig - Настройки базы данных
        secret_key: str - Секретный ключ для шифрования данных
        debug: bool - Флаг для включения режима отладки
        algorithm: str -- Алгоритм шифрования
        access_token_expire_minutes: int -- Длительность работы Access Token
    """

    db: DatabaseConfig
    debug: bool
    secret_key: str  # JWT
    algorithm: str = "HS256"  # Алгоритм шифрования
    access_token_expire_minutes: int = 60 * 24  # 24 часа


def _get_required_env(key: str) -> str:
    """
    Получение переменной окружения, которая является обязательной.
    Args:
        key: str - Ключ переменной окружения.

    Returns:
        str -- Значение переменной окружения.
    """
    value = os.getenv(key)
    if value is None:
        raise RuntimeError(f"Обязательная переменная окружения {key} не установлена.")
    return value


def load_config() -> Config:
    """
    Загрузка конфигурации из .env файла, который по умолчанию находится в корне проекта.
    Returns:
        Config - Загруженная конфигурация приложения.
    """
    env_path = Path(__file__).parent.parent.parent / ".env"  # Путь к .env файлу в корне проекта
    load_dotenv(env_path)
    return Config(
        db=DatabaseConfig(_get_required_env("DATABASE_URL")),
        secret_key=_get_required_env("SECRET_KEY"),
        debug=os.getenv("DEBUG", default="True") in ("True", "true", "1"),
        algorithm=os.getenv("ALGORITHM", default="HS256"),
        access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", default=60 * 24)),
    )
