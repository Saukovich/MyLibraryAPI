from fastapi import APIRouter, Depends

from app.schemas.book_schemas import BookCreate, BookResponse, BookUpdate, PopularBookResponse
from app.schemas.params import BookFilterParams
from app.services.book_service import BookService


router = APIRouter(prefix="/books", tags=["books"])


@router.get("/", status_code=200, response_model=list[BookResponse])
async def get_books(book_filter_params: BookFilterParams = Depends(), book_service: BookService = Depends()):
    """
    Получение списка книг по фильтрам.

    Если фильтры не указаны, то возвращаются все книги.
    """
    books = await book_service.get_by_filters(book_filter_params)
    return books


@router.get("/popular", status_code=200, response_model=list[PopularBookResponse])
async def get_popular_books(limit: int = 10, book_service: BookService = Depends()):
    """
    Получение популярных книг.

    По умолчанию возвращается 10 популярных книг (на основе кол-ва добавлений на полки пользоваетелй и средний рейтинг).
    """
    popular_books = await book_service.get_popular(limit)
    return popular_books


@router.get(
    "/{book_id}", status_code=200, response_model=BookResponse, responses={404: {"description": "Книга не найдена."}}
)
async def get_book(book_id: int, book_service: BookService = Depends()):
    """
    Получение книги по ID.
    """
    book = await book_service.get_by_id(book_id)
    return book


@router.post("/", status_code=201, response_model=BookResponse, responses={404: {"description": "Автор не найден."}})
async def create_book(book: BookCreate, book_service: BookService = Depends()):
    """
    Создание книги.

    Если автора не существует, то он будет создан. Передается либо ID существующего автора, либо данные для его создания.
    """
    book = await book_service.create(book)
    return book


@router.put(
    "/{book_id}",
    status_code=200,
    response_model=BookResponse,
    responses={404: {"description": "Книга не найдена / Автор не найден."}},
)
async def put_book(book_id: int, book: BookCreate, book_service: BookService = Depends()):
    """
    Полное обновление книги.

    Если автора не существует, то он будет создан. Передается либо ID существующего автора, либо данные для его создания.
    """
    book = await book_service.replace(book_id, book)
    return book


@router.patch(
    "/{book_id}",
    status_code=200,
    response_model=BookResponse,
    responses={404: {"description": "Книга не найдена / Автор не найден."}},
)
async def patch_book(book_id: int, book: BookUpdate, book_service: BookService = Depends()):
    """
    Частичное обновление книги.

    Если автора не существует, то он будет создан. Передается либо ID существующего автора, либо данные для его создания.
    """
    book = await book_service.update(book_id, book)
    return book


@router.delete("/{book_id}", status_code=204, responses={404: {"description": "Книга не найдена."}})
async def delete_book(book_id: int, book_service: BookService = Depends()):
    """
    Удаление книги.
    """
    await book_service.delete(book_id)
