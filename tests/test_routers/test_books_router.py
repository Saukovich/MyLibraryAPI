import pytest


@pytest.mark.asyncio
async def test_books_router_get_books_happy_path(client, book):
    """Тест эндопоинта GET /api/v1/books/."""
    response = await client.get("api/v1/books/")
    assert response.status_code == 200
    assert response.json()[0]["title"] == "Test Book"


@pytest.mark.asyncio
async def test_books_router_get_popular_books_happy_path(client, shelf_entry):
    """Тест эндопоинта GET /api/v1/books/popular."""
    response = await client.get("api/v1/books/popular")
    assert response.status_code == 200
    assert response.json()[0]["title"] == "Test Book"
    assert response.json()[0]["number_of_additions"] == 1
    assert response.json()[0]["avg_rating"] is None


@pytest.mark.asyncio
async def test_books_router_get_by_id_happy_path(client, book):
    """Тест эндопоинта GET /api/v1/books/{id}."""
    response = await client.get(f"api/v1/books/{book.id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Book"


@pytest.mark.asyncio
async def test_books_router_get_by_id_not_found(client):
    """Тест эндопоинта GET /api/v1/books/{id} с несуществующей книгой."""
    response = await client.get("api/v1/books/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_books_router_create_book_happy_path(client, author):
    """Тест эндопоинта POST /api/v1/books/."""
    response = await client.post(
        "api/v1/books/", json={"title": "Test Book 2", "release_year": 2023, "authors": [{"id": author.id}]}
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test Book 2"
    assert response.json()["authors"][0] == "Test Author"
    assert response.json()["release_year"] == 2023


@pytest.mark.asyncio
async def test_books_router_create_book_author_not_found(client):
    """Тест эндопоинта POST /api/v1/books/ с несуществующим автором."""
    response = await client.post(
        "api/v1/books/", json={"title": "Test Book 2", "release_year": 2023, "authors": [{"id": 99999}]}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_books_router_put_happy_path(client, book):
    """Тест эндопоинта PUT /api/v1/books/{id}."""
    response = await client.put(
        f"api/v1/books/{book.id}",
        json={
            "title": "Test Book 2",
            "release_year": 2026,
            "authors": [{"fullname": "Test Author 2", "birth_year": 2000}],
        },
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Test Book 2"
    assert response.json()["release_year"] == 2026
    assert response.json()["authors"][0] == "Test Author 2"


@pytest.mark.asyncio
async def test_books_router_put_book_book_not_found(client):
    """Тест эндопоинта PUT /api/v1/books/{id} с несуществующей книгой."""
    response = await client.put(
        "api/v1/books/99999",
        json={
            "title": "Test Book 2",
            "release_year": 2026,
            "authors": [{"fullname": "Test Author 2", "birth_year": 2000}],
        },
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_books_router_put_book_author_not_found(client, book):
    """Тест эндопоинта PUT /api/v1/books/{id} с несуществующим автором."""
    response = await client.put(
        f"api/v1/books/{book.id}", json={"title": "Test Book 2", "release_year": 2026, "authors": [{"id": 99999}]}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_books_router_patch_book_happy_path(client, book):
    """Тест эндопоинта PATCH /api/v1/books/{id}."""
    response = await client.patch(f"api/v1/books/{book.id}", json={"title": "Test Book 2"})
    assert response.status_code == 200
    assert response.json()["title"] == "Test Book 2"


@pytest.mark.asyncio
async def test_books_router_patch_book_book_not_found(client):
    """Тест эндопоинта PATCH /api/v1/books/{id} с несуществующей книгой."""
    response = await client.patch("api/v1/books/99999", json={"title": "Test Book 2"})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_books_router_patch_book_author_not_found(client):
    """Тест эндопоинта PATCH /api/v1/books/{id} с несуществующим автором."""
    response = await client.patch("api/v1/books/99999", json={"authors": [{"id": 99999}]})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_books_router_delete_book_happy_path(client, book):
    """Тест эндопоинта DELETE /api/v1/books/{id}."""
    response = await client.delete(f"api/v1/books/{book.id}")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_books_router_delete_book_not_found(client):
    """Тест эндопоинта DELETE /api/v1/books/{id} с несуществующей книгой."""
    response = await client.delete("api/v1/books/99999")
    assert response.status_code == 404
