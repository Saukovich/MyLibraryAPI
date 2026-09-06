import pytest


@pytest.mark.asyncio
async def test_authors_router_get_authors_happy_path(client, author):
    """Тест эндпоинта GET /api/v1/authors/"""
    response = await client.get("api/v1/authors/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["fullname"] == "Test Author"


@pytest.mark.asyncio
async def test_authors_router_get_author_happy_path(client, author):
    """Тест эндпоинта GET /api/v1/authors/{author_id}"""
    response = await client.get(f"api/v1/authors/{author.id}")
    assert response.status_code == 200
    assert response.json()["fullname"] == "Test Author"
    assert response.json()["birth_year"] == 1990
    assert response.json()["death_year"] == 2020


@pytest.mark.asyncio
async def test_authors_router_get_author_not_found_status_code_404(client):
    """Тест эндпоинта GET /api/v1/authors/{author_id} с несуществующим автором"""
    response = await client.get("api/v1/authors/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_authors_router_get_author_books_happy_path(client, author, book):
    """Тест эндпоинта GET /api/v1/authors/{author_id}/books"""
    response = await client.get(f"api/v1/authors/{author.id}/books")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Test Book"
    assert response.json()[0]["release_year"] == 2020


@pytest.mark.asyncio
async def test_authors_router_create_author_happy_path(client):
    """Тест эндпоинта POST /api/v1/authors/"""
    response = await client.post(
        "api/v1/authors/", json={"fullname": "New Author", "birth_year": 1990, "death_year": 2020}
    )
    assert response.status_code == 201
    assert response.json()["fullname"] == "New Author"
    assert response.json()["birth_year"] == 1990
    assert response.json()["death_year"] == 2020


@pytest.mark.asyncio
async def test_authors_router_replace_author_happy_path(client, author):
    """Тест эндпоинта PUT /api/v1/authors/{author_id}"""
    response = await client.put(
        f"api/v1/authors/{author.id}", json={"fullname": "Replaced Author", "birth_year": 2000, "death_year": 2021}
    )
    assert response.status_code == 200
    assert response.json()["fullname"] == "Replaced Author"
    assert response.json()["birth_year"] == 2000
    assert response.json()["death_year"] == 2021


@pytest.mark.asyncio
async def test_authors_router_replace_author_not_found_status_code_404(client):
    """Тест эндпоинта PUT /api/v1/authors/{author_id} с несуществующим автором"""
    response = await client.put(
        "api/v1/authors/999", json={"fullname": "Replaced Author", "birth_year": 2000, "death_year": 2021}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_authors_router_update_author_happy_path(client, author):
    """Тест эндпоинта PATCH /api/v1/authors/{author_id}"""
    response = await client.patch(f"api/v1/authors/{author.id}", json={"fullname": "Updated Author"})
    assert response.status_code == 200
    assert response.json()["fullname"] == "Updated Author"


@pytest.mark.asyncio
async def test_authors_router_update_author_not_found_status_code_404(client):
    """Тест эндпоинта PATCH /api/v1/authors/{author_id} с несуществующим автором"""
    response = await client.patch("api/v1/authors/999", json={"fullname": "Updated Author"})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_authors_router_delete_author_happy_path(client, author):
    """Тест эндпоинта DELETE /api/v1/authors/{author_id}"""
    response = await client.delete(f"api/v1/authors/{author.id}")
    assert response.status_code == 204

    response = await client.get(f"api/v1/authors/{author.id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_authors_router_delete_author_not_found_status_code_404(client):
    """Тест эндпоинта DELETE /api/v1/authors/{author_id} с несуществующим автором"""
    response = await client.delete("api/v1/authors/999")
    assert response.status_code == 404
