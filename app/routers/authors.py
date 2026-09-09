from fastapi import APIRouter, Depends

from app.schemas.author_schemas import AuthorCreate, AuthorResponse, AuthorUpdate
from app.schemas.book_schemas import BookResponse
from app.schemas.params import AuthorFilterParams, BookFilterParams
from app.services.author_service import AuthorService
from app.services.book_service import BookService


router = APIRouter(prefix="/authors", tags=["authors"])


@router.get("/", status_code=200, response_model=list[AuthorResponse])
async def get_authors(author_filter_params: AuthorFilterParams = Depends(), author_service: AuthorService = Depends()):
    """
    Получение всех авторов по фильтрам.
    """
    authors = await author_service.get_by_filters(author_filter_params)
    return authors


@router.get(
    "/{author_id}", status_code=200, response_model=AuthorResponse, responses={404: {"description": "Автор не найден."}}
)
async def get_author(author_id: int, author_service: AuthorService = Depends()):
    """
    Получение автора по ID.
    """
    author = await author_service.get_by_id(author_id)
    return author


@router.get("/{author_id}/books", status_code=200, response_model=list[BookResponse])
async def get_author_books(
    author_id: int, book_filter_params: BookFilterParams = Depends(), book_service: BookService = Depends()
):
    """
    Получение всех книг автора по ID.

    Возвращает все книги автора по ID с фильтрацией для книг. Если в query-параметрах
    явно указать 'author_id' или 'author_name', то фильтрация по этим параметрам будет игнорироваться.
    'author_id' берется из URL-параметра.
    """
    book_filter_params.author_id = author_id
    book_filter_params.author_name = None

    books = await book_service.get_by_filters(book_filter_params)
    return books


@router.post("/", status_code=201, response_model=AuthorResponse)
async def create_author(data: AuthorCreate, author_service: AuthorService = Depends()):
    """
    Создание нового автора.
    """
    author = await author_service.create(data)
    return author


@router.put(
    "/{author_id}", status_code=200, response_model=AuthorResponse, responses={404: {"description": "Автор не найден."}}
)
async def put_author(author_id: int, data: AuthorCreate, author_service: AuthorService = Depends()):
    """
    Полное обновление автора по ID.
    """
    author = await author_service.replace(author_id, data)
    return author


@router.patch(
    "/{author_id}", status_code=200, response_model=AuthorResponse, responses={404: {"description": "Автор не найден."}}
)
async def patch_author(author_id: int, data: AuthorUpdate, author_service: AuthorService = Depends()):
    """
    Частичное обновление автора по ID.
    """
    author = await author_service.update(author_id, data)
    return author


@router.delete("/{author_id}", status_code=204, responses={404: {"description": "Автор не найден."}})
async def delete_author(author_id: int, author_service: AuthorService = Depends()):
    """
    Удаление автора по ID.
    """
    await author_service.delete(author_id)
