import pytest
from fastapi import HTTPException

from app.repositories.author_repository import AuthorRepository
from app.schemas.author_schemas import AuthorCreate, AuthorUpdate
from app.services.author_service import AuthorService


@pytest.fixture
def author_service(db_session):
    """Фикстура для создания экземпляра AuthorService."""
    author_repository = AuthorRepository(db_session)
    return AuthorService(author_repository)


@pytest.mark.asyncio
async def test_author_service_get_by_id_happy_path(author_service):
    """Тест получения автора по ID."""
    author_create = AuthorCreate(fullname="Test Author", birth_year=1990)
    author = await author_service.create(author_create)
    got_author = await author_service.get_by_id(author.id)

    assert got_author.id == author.id


@pytest.mark.asyncio
async def test_author_service_get_by_id_not_found_raises_404(author_service):
    """Тест получения несуществующего автора. Вызывает исключение с кодом 404."""
    with pytest.raises(HTTPException) as exc_info:
        await author_service.get_by_id(999999)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_author_service_update_happy_path(author_service):
    """Тест частичного обновления автора."""
    author_create = AuthorCreate(fullname="Test Author", birth_year=1990)
    author = await author_service.create(author_create)

    author_update = AuthorUpdate(fullname="Updated Author")
    updated_author = await author_service.update(author.id, author_update)

    assert updated_author.fullname == "Updated Author"


@pytest.mark.asyncio
async def test_author_service_update_not_found_raises_404(author_service):
    """Тест частичного обновления несуществующего автора. Вызывает исключение с кодом 404."""
    author_update = AuthorUpdate(fullname="Updated Author")
    with pytest.raises(HTTPException) as exc_info:
        await author_service.update(99999, author_update)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_author_service_replace_happy_path(author_service):
    """Тест полного обновления автора."""
    author_create = AuthorCreate(fullname="Test Author", birth_year=1990)
    author = await author_service.create(author_create)

    author_replace = AuthorCreate(fullname="Updated Author", birth_year=2010)
    replaced_author = await author_service.replace(author.id, author_replace)

    assert replaced_author.fullname == "Updated Author" and replaced_author.birth_year == 2010


@pytest.mark.asyncio
async def test_author_service_replace_not_found_raises_404(author_service):
    """Тест полного обновления несуществующего автора. Вызывает исключение с кодом 404."""
    author_replace = AuthorCreate(fullname="Updated Author", birth_year=2010)
    with pytest.raises(HTTPException) as exc_info:
        await author_service.replace(99999, author_replace)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_author_service_delete_happy_path(author_service):
    """Тест удаления автора."""
    author_create = AuthorCreate(fullname="Test Author", birth_year=1990)
    author = await author_service.create(author_create)

    await author_service.delete(author.id)

    with pytest.raises(HTTPException) as exc_info:
        await author_service.get_by_id(author.id)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_author_service_delete_not_found_raises_404(author_service):
    """Тест удаления несуществующего автора. Вызывает исключение с кодом 404."""
    with pytest.raises(HTTPException) as exc_info:
        await author_service.delete(99999)
    assert exc_info.value.status_code == 404
