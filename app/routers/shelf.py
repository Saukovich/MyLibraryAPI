from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.models.users import User
from app.schemas.params import ShelfFilterParams
from app.schemas.shelf_schemas import ShelfEntryCreate, ShelfEntryResponse, ShelfEntryUpdate, ShelfStatsResponse
from app.services.shelf_service import ShelfService


router = APIRouter(prefix="/users/me/books", tags=["shelf"])


@router.get(
    "/",
    status_code=200,
    response_model=list[ShelfEntryResponse],
    responses={401: {"description": "Пользователь не авторизован."}},
)
async def get_shelf_entries(
    shelf_filter_params: ShelfFilterParams = Depends(),
    current_user: User = Depends(get_current_user),
    shelf_service: ShelfService = Depends(),
):
    """
    Получение списка книг на полке.
    """
    shelf_entries = await shelf_service.get_by_filters(current_user.id, shelf_filter_params)
    return shelf_entries


@router.get(
    "/stats",
    status_code=200,
    response_model=ShelfStatsResponse,
    responses={401: {"description": "Пользователь не авторизован."}},
)
async def get_shelf_stats(current_user: User = Depends(get_current_user), shelf_service: ShelfService = Depends()):
    """
    Получение статистики полки.

    Возвращает количество книг на полке, средний рейтинг и любимого автора (на основе кол-ва книг этого автора на полке).
    """
    stats = await shelf_service.get_stats(current_user.id)
    return stats


@router.get(
    "/{book_id}",
    status_code=200,
    response_model=ShelfEntryResponse,
    responses={
        401: {"description": "Пользователь не авторизован."},
        404: {"description": "Книга не найдена / Книга на полке не найдена."},
    },
)
async def get_shelf_entry(
    book_id: int, current_user: User = Depends(get_current_user), shelf_service: ShelfService = Depends()
):
    """
    Получение книги на полке по ID книги.
    """
    shelf_entry = await shelf_service.get_by_id(current_user.id, book_id)
    return shelf_entry


@router.post(
    "/{book_id}",
    status_code=201,
    response_model=ShelfEntryResponse,
    responses={404: {"description": "Книга не найдена."}, 409: {"description": "Книга уже есть на полке."}},
)
async def add_book_to_shelf(
    book_id: int,
    shelf_entry: ShelfEntryCreate,
    current_user: User = Depends(get_current_user),
    shelf_service: ShelfService = Depends(),
):
    """
    Добавление книги на полку.

    Если книга уже есть на полке, вызывает исключение с кодом 409.
    """
    shelf_entry = await shelf_service.create(current_user.id, book_id, shelf_entry)
    return shelf_entry


@router.put(
    "/{book_id}",
    status_code=200,
    response_model=ShelfEntryResponse,
    responses={
        401: {"description": "Пользователь не авторизован."},
        404: {"description": "Книга не найдена / Книга на полке не найдена."},
    },
)
async def put_shelf_entry(
    book_id: int,
    shelf_entry: ShelfEntryCreate,
    current_user: User = Depends(get_current_user),
    shelf_service: ShelfService = Depends(),
):
    """
    Полночное обновление книги на полке.

    Рейтинг может быть установлен только для прочитанных книг.
    """
    shelf_entry = await shelf_service.replace(current_user.id, book_id, shelf_entry)
    return shelf_entry


@router.patch(
    "/{book_id}",
    status_code=200,
    response_model=ShelfEntryResponse,
    responses={
        401: {"description": "Пользователь не авторизован."},
        404: {"description": "Книга не найдена / Книга на полке не найдена."},
        400: {"description": "Рейтинг может быть установлен только для прочитанных книг."},
    },
)
async def patch_shelf_entry(
    book_id: int,
    shelf_entry: ShelfEntryUpdate,
    current_user: User = Depends(get_current_user),
    shelf_service: ShelfService = Depends(),
):
    """
    Частичное обновление книги на полке.

    Рейтинг может быть установлен только для прочитанных книг.
    """
    shelf_entry = await shelf_service.update(current_user.id, book_id, shelf_entry)
    return shelf_entry


@router.delete(
    "/{book_id}",
    status_code=204,
    responses={
        401: {"description": "Пользователь не авторизован."},
        404: {"description": "Книги не найдена / Книга на полке не найдена."},
    },
)
async def delete_shelf_entry(
    book_id: int, current_user: User = Depends(get_current_user), shelf_service: ShelfService = Depends()
):
    """
    Удаление книги с полки.
    """
    await shelf_service.delete(current_user.id, book_id)
