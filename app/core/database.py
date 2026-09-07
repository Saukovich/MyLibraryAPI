from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass

from .config import load_config


config = load_config()
DATABASE_URL = config.db.database_url


engine = create_async_engine(DATABASE_URL)
new_session = async_sessionmaker(engine, expire_on_commit=False)

naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Model(MappedAsDataclass, DeclarativeBase):
    """
    Базовая модель для всех моделей SQLAlchemy.
    """

    metaclass = MetaData(naming_convention=naming_convention)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Создает асинхронную сессию для работы с базой данных.
    :yield: AsyncSession - асинхронная сессия для работы с базой данных.
    """
    async with new_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# Тип для зависимости от сессии, который будет использоваться в эндпоинтах
SessionDep = Annotated[AsyncSession, Depends(get_db)]
