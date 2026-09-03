from fastapi import HTTPException

from app.core.security import create_access_token, hash_password, verify_password
from app.models.users import User
from app.repositories.user_repository import UserRepository
from app.schemas.user_schemas import UserLoginRequest, UserRegisterRequest


class AuthService:
    """
    Сервис авторизации.
    """

    def __init__(self, user_repository: UserRepository) -> None:
        """
        Инициализация сервиса авторизации.
        Args:
            user_repository: UserRepository -- репозиторий пользователей.
        """
        self.user_repository = user_repository

    async def register(self, data: UserRegisterRequest) -> User:
        """
        Регистрация пользователя.
        Args:
            data: UserRegisterRequest -- данные для регистрации.

        Returns:
            User -- созданный пользователь.
        """
        if await self.user_repository.exists_user_by_username(data.username):
            raise HTTPException(status_code=409, detail="Username уже занят.")
        if await self.user_repository.exists_user_by_email(data.email):
            raise HTTPException(status_code=409, detail="Email уже занят.")

        hashed = hash_password(data.password)
        return await self.user_repository.create(
            {"username": data.username, "email": data.email, "password_hash": hashed}
        )

    async def login(self, data: UserLoginRequest) -> str:
        """
        Авторизация пользователя.
        Args:
            data: UserLoginRequest -- данные для авторизации.

        Returns:
            str -- JWT токен.
        """
        user = await self._find_user(data.username, data.email)
        if user is None or not verify_password(data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials.")

        return create_access_token(user_id=user.id)

    async def get_me(self, user_id: int) -> User:
        """
        Получение пользователя по id.
        Args:
            user_id: int -- id пользователя.

        Returns:
            User -- найденный пользователь.
        """
        user = await self.user_repository.get_by_id(id=user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found.")
        return user

    async def _find_user(self, username: str | None, email: str | None) -> User | None:
        """
        Вспомогательный метод для поиска пользователя по username или email.
        Args:
            username: str | None -- username пользователя.
            email: str | None -- email пользователя.

        Returns:
            User | None -- найденный пользователь.
        """
        if username is not None:
            return await self.user_repository.get_user_by_username(username)
        if email is not None:
            return await self.user_repository.get_user_by_email(email)
        return None
