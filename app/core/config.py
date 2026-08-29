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
    """

    db: DatabaseConfig
    debug: bool
    secret_key: str  # JWT
    algorithm: str = "HS256"  # Алгоритм шифрования
    access_token_expire_minutes: int = 60 * 24  # 24 часа


def load_config() -> Config:
    """
    Загрузка конфигурации из .env файла, который по умолчанию находится в корне проекта.
    :return: Config - Загруженная конфигурация приложения.
    """
    env_path = Path(__file__).parent.parent.parent / ".env"  # Путь к .env файлу в корне проекта
    load_dotenv(env_path)
    return Config(
        db=DatabaseConfig(os.getenv("DATABASE_URL")),
        secret_key=os.getenv("SECRET_KEY"),
        debug=os.getenv("DEBUG", default=True),
    )
