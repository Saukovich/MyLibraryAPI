import asyncio

import pytest
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Model


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:?foreign_keys=on"

engine = create_async_engine(TEST_DATABASE_URL)
testing_session = async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture(scope="session")
async def event_loop():
    """
    Создание цикла событий для тестов.
    :return: AbstractEventLoop - цикл событий.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()  # создание цикла событий
    yield loop
    loop.close()


@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Включение поддержки внешних ключей в SQLite.
    :param dbapi_connection: Connection - соединение.
    :param connection_record: ConnectionRecord - запись соединения.
    :return: None.
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture(autouse=True, scope="function")
async def setup_database():
    """
    Создание тестовой базы данных и удаление всех таблиц после тестов.
    :return: None.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)  # создание таблиц
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)  # удаление таблиц


@pytest.fixture
async def db_session() -> AsyncSession:
    """
    Создание сессии для работы с тестовой базой данных.
    :return: AsyncGenerator[AsyncSession, None] - сессия.
    """
    async with testing_session() as session:
        yield session
