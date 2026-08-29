import pytest

from app.models.authors import Author
from app.repositories.base_repository import BaseRepository


@pytest.fixture
def base_repo(db_session):
    return BaseRepository(Author, db_session)


@pytest.mark.asyncio
async def test_base_repo_create_and_get(base_repo):
    """Тест создания и получения автора."""
    author = await base_repo.create({"fullname": "Stephen King", "birth_year": 1947})

    assert author.id is not None
    assert author.fullname == "Stephen King"

    db_author = await base_repo.get_by_id(id=author.id)
    assert db_author is not None
    assert db_author.id == author.id


@pytest.mark.asyncio
async def test_base_repo_get_all(base_repo):
    """Тест получения всех авторов."""
    for i in range(5):
        await base_repo.create({"fullname": f"Stephen King #{i}", "birth_year": 1947})

    authors = await base_repo.get_all()
    assert len(authors) == 5


@pytest.mark.asyncio
async def test_base_repo_delete(base_repo):
    """Тест удаления автора."""
    for i in range(5):
        await base_repo.create({"fullname": f"Stephen King #{i}", "birth_year": 1947})

    authors_before_delete = await base_repo.get_all()

    await base_repo.delete(id=authors_before_delete[0].id)

    authors_after_delete = await base_repo.get_all()

    assert len(authors_before_delete) - 1 == len(authors_after_delete)


@pytest.mark.asyncio
async def test_base_repo_update(base_repo):
    """Тест обновления автора."""
    author_before_update = await base_repo.create({"fullname": "Stephen King", "birth_year": 1947})
    author_fullname_before_update = author_before_update.fullname
    author_after_update = await base_repo.update(id=author_before_update.id, data={"fullname": "Stephen King 2"})

    assert author_before_update.id == author_after_update.id
    assert author_fullname_before_update != author_after_update.fullname
    assert author_after_update.fullname == "Stephen King 2"
