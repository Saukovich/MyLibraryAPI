from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass

from .config import load_config


config = load_config()
DATABASE_URL = config.db.database_url


engine = create_async_engine(DATABASE_URL)
new_session = async_sessionmaker(engine, expire_on_commit=False)


class Model(MappedAsDataclass, DeclarativeBase):
    """
    Базовая модель для всех моделей SQLAlchemy.
    """

    pass


async def get_db() -> AsyncSession:
    """
    Создает асинхронную сессию для работы с базой данных.
    :return: AsyncSession - асинхронная сессия для работы с базой данных.
    """
    async with new_session() as session:
        yield session


# Тип для зависимости от сессии, который будет использоваться в эндпоинтах
SessionDep = Annotated[AsyncSession, Depends(get_db)]
