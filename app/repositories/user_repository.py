from sqlalchemy import exists, select

from app.core.database import SessionDep
from app.models.users import User

from .base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Класс репозитория для работы с пользователями."""

    def __init__(self, session: SessionDep):
        """
        Инициализация репозитория.
        Args:
            session: SessionDep -- сессия базы данных.
        """
        super().__init__(User, session)

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Получить пользователя по имени пользователя.
        Args:
            username: str -- имя пользователя.

        Returns:
            User | None -- пользователь или None, если не найден.
        """
        query = select(User).where(User.username == username)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Получить пользователя по email.
        Args:
            email: str -- email пользователя.

        Returns:
            User | None -- пользователь или None, если не найден.
        """
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def exists_user_by_username(self, username: str) -> bool:
        """
        Проверить, существует ли пользователь с таким именем пользователя.
        Args:
            username: str -- имя пользователя.

        Returns:
            Bool -- True, если существует, иначе False.
        """
        query = select(exists().where(User.username == username))
        return await self.session.scalar(query)

    async def exists_user_by_email(self, email: str) -> bool:
        """
        Проверить, существует ли пользователь с таким email.
        Args:
            email: str -- email пользователя.

        Returns:
            Bool -- True, если существует, иначе False.
        """
        query = select(exists().where(User.email == email))
        return await self.session.scalar(query)
