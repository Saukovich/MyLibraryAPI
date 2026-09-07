from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.models.users import User
from app.schemas.user_schemas import TokenResponse, UserLoginRequest, UserRegisterRequest, UserResponse
from app.services.auth_service import AuthService


router = APIRouter(tags=["auth"])


@router.post(
    "/login",
    status_code=200,
    response_model=TokenResponse,
    responses={401: {"description": "Такого пользователя не существует или пароль неверен."}},
)
async def login(data: UserLoginRequest, auth_service: AuthService = Depends()):
    """
    Идентификация и аутентификация пользователя.
    """
    access_token = await auth_service.login(data)
    response = TokenResponse(access_token=access_token)
    return response


@router.post(
    "/register",
    status_code=201,
    response_model=UserResponse,
    responses={409: {"description": "Пользователь с таким username/email уже существует."}},
)
async def register(data: UserRegisterRequest, auth_service: AuthService = Depends()):
    """
    Регистрация нового пользователя.
    """
    user = await auth_service.register(data)
    return user


@router.get(
    "/users/me",
    status_code=200,
    response_model=UserResponse,
    responses={401: {"description": "Пользователь не авторизован."}},
)
async def get_me(current_user: User = Depends(get_current_user), auth_service: AuthService = Depends()):
    """
    Получение информации о текущем пользователе.
    """
    return await auth_service.get_me(current_user.id)
