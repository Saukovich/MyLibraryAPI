from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.models.users import User
from app.schemas.notes_schemas import NoteCreate, NoteResponse, NoteUpdate
from app.schemas.params import NoteFilterParams
from app.services.note_service import NoteService


router = APIRouter(prefix="/users/me/books/{book_id}/notes", tags=["notes"])


@router.get(
    "/",
    status_code=200,
    response_model=list[NoteResponse],
    responses={
        401: {"description": "Пользователь не авторизован."},
        404: {"description": "Книга не найдена / Книги нет на полке."},
    },
)
async def get_notes(
    book_id: int,
    current_user: User = Depends(get_current_user),
    note_filter_params: NoteFilterParams = Depends(),
    note_service: NoteService = Depends(),
):
    """
    Получение списка заметок для книги на полке пользователя.
    """
    notes = await note_service.get_by_shelf_entry(current_user.id, book_id, note_filter_params)
    return notes


@router.get(
    "/{note_id}",
    status_code=200,
    response_model=NoteResponse,
    responses={
        401: {"description": "Пользователь не авторизован."},
        404: {"description": "Книга не найдена / Книги нет на полке."},
    },
)
async def get_note(
    book_id: int, note_id: int, current_user: User = Depends(get_current_user), note_service: NoteService = Depends()
):
    """
    Получение заметки по ID.
    """
    note = await note_service.get_by_id(current_user.id, book_id, note_id)
    return note


@router.post(
    "/",
    status_code=201,
    response_model=NoteResponse,
    responses={
        401: {"description": "Пользователь не авторизован."},
        404: {"description": "Книга не найдена / Книги нет на полке."},
    },
)
async def create_note(
    book_id: int,
    data: NoteCreate,
    current_user: User = Depends(get_current_user),
    note_service: NoteService = Depends(),
):
    """
    Создание заметки для книги на полке пользователя.
    """
    note = await note_service.create(current_user.id, book_id, data)
    return note


@router.put(
    "/{note_id}",
    status_code=200,
    response_model=NoteResponse,
    responses={
        401: {"description": "Пользователь не авторизован"},
        404: {"description": "Книга не найдена / Книги нет на полке / Заметка не найдена."},
    },
)
async def put_note(
    book_id: int,
    note_id: int,
    data: NoteCreate,
    current_user: User = Depends(get_current_user),
    note_service: NoteService = Depends(),
):
    """
    Полное обновление заметки для книги на полке пользователя.
    """
    note = await note_service.replace(current_user.id, book_id, note_id, data)
    return note


@router.patch(
    "/{note_id}",
    status_code=200,
    response_model=NoteResponse,
    responses={
        401: {"description": "Пользователь не авторизован"},
        404: {"description": "Книга не найдена / Книги нет на полке / Заметка не найдена."},
    },
)
async def patch_note(
    book_id: int,
    note_id: int,
    data: NoteUpdate,
    current_user: User = Depends(get_current_user),
    note_service: NoteService = Depends(),
):
    """
    Частичное обновление заметки для книги на полке пользователя.
    """
    note = await note_service.update(current_user.id, book_id, note_id, data)
    return note


@router.delete(
    "/{note_id}",
    status_code=204,
    responses={
        401: {"description": "Пользователь не авторизован"},
        404: {"description": "Книга не найдена / Книги нет на полке / Заметка не найдена."},
    },
)
async def delete_note(
    book_id: int, note_id: int, current_user: User = Depends(get_current_user), note_service: NoteService = Depends()
):
    """
    Удаление заметки для книги на полке пользователя.
    """
    await note_service.delete(current_user.id, book_id, note_id)
