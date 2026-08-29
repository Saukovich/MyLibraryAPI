from typing import Generic, Sequence, Type, TypeVar

from sqlalchemy import delete, select, update

from app.core.database import SessionDep


ModelType = TypeVar("ModelType")  # Тип для модели


class BaseRepository(Generic[ModelType]):
    """Базовый репозиторий."""

    def __init__(self, model: Type[ModelType], session: SessionDep) -> None:
        """
        Инициализация репозитория.
        Args:
            model: Type[ModelType] -- тип модели.
            session: SessionDep -- сессия базы данных.
        """
        self.model = model
        self.session = session

    async def get_by_id(self, **composite_id) -> ModelType | None:
        """
        Получение объекта по его идентификатору.
        Args:
            **composite_id: словарь с идентификаторами объекта.

        Returns:
            ModelType | None -- объект или None, если объект не найден.
        """
        query = select(self.model).filter_by(**composite_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, limit: int = 100, offset: int = 0) -> Sequence[ModelType] | None:
        """
        Получение всех объектов.
        Args:
            limit: int -- максимальное количество объектов.
            offset: int -- смещение.

        Returns:
            Sequence[ModelType] | None -- список объектов или None, если объекты не найдены.
        """
        query = select(self.model).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, data: dict) -> ModelType:
        """
        Создание объекта.
        Args:
            data: dict -- данные для создания объекта.

        Returns:
            ModelType -- созданный объект.
        """
        db_obj = self.model(**data)

        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)

        return db_obj

    async def update(self, data: dict, **composite_id) -> ModelType:
        """
        Обновление объекта.
        Args:
            data: dict -- данные для обновления объекта.
            **composite_id: словарь с идентификаторами объекта.

        Returns:
            ModelType -- обновленный объект.
        """
        query = update(self.model).filter_by(**composite_id).values(**data).returning(self.model)

        result = await self.session.execute(query)
        await self.session.flush()

        return result.scalar_one_or_none()

    async def delete(self, **composite_id) -> bool:
        """
        Удаление объекта.
        Args:
            **composite_id: словарь с идентификаторами объекта.

        Returns:
            book: bool -- True, если объект удален, иначе False.
        """
        query = delete(self.model).filter_by(**composite_id)

        result = await self.session.execute(query)
        await self.session.flush()

        return result.rowcount > 0
