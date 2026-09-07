import pytest

from app.models.enums import BookStatus


@pytest.mark.asyncio
async def test_shelf_router_get_shelf_entries_happy_path(authenticated_client, shelf_entry, book):
    """Тест эндпоинта GET /api/v1/users/me/books/."""
    response = await authenticated_client.get("api/v1/users/me/books/")
    assert response.status_code == 200
    assert response.json()[0]["title"] == book.title
    assert response.json()[0]["authors"][0] == book.authors[0].fullname
    assert response.json()[0]["book_id"] == book.id
    assert response.json()[0]["status"] == shelf_entry.status.value


@pytest.mark.asyncio
async def test_shelf_router_get_shelf_entries_unauthorized(client):
    """Тест эндпоинта GET /api/v1/users/me/books/ без авторизации."""
    response = await client.get("api/v1/users/me/books/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_shelf_router_get_shelf_stats_happy_path(authenticated_client, author, shelf_entry):
    """Тест эндпоинта GET /api/v1/users/me/books/stats/."""
    response = await authenticated_client.get("api/v1/users/me/books/stats")
    assert response.status_code == 200
    assert response.json()["number_of_books"] == 1
    assert response.json()["avg_rating"] is None
    assert response.json()["favorite_author"] == author.fullname


@pytest.mark.asyncio
async def test_shelf_router_get_shelf_stats_unauthorized(client):
    """Тест эндпоинта GET /api/v1/users/me/books/stats/ без авторизации."""
    response = await client.get("api/v1/users/me/books/stats")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_shelf_router_get_shelf_entry_happy_path(authenticated_client, shelf_entry):
    """Тест эндпоинта GET /api/v1/users/me/books/{book_id}."""
    response = await authenticated_client.get(f"api/v1/users/me/books/{shelf_entry.book_id}")
    assert response.status_code == 200
    assert response.json()["title"] == shelf_entry.book.title
    assert response.json()["authors"][0] == shelf_entry.book.authors[0].fullname
    assert response.json()["book_id"] == shelf_entry.book.id
    assert response.json()["status"] == shelf_entry.status.value
    assert response.json()["rating"] is shelf_entry.rating


@pytest.mark.asyncio
async def test_shelf_router_get_shelf_entry_book_not_found(authenticated_client):
    """Тест эндпоинта GET /api/v1/users/me/books/{book_id} для несуществующей книги."""
    response = await authenticated_client.get("api/v1/users/me/books/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_shelf_router_get_shelf_entry_unauthorized(client, shelf_entry):
    """Тест эндпоинта GET /api/v1/users/me/books/{book_id} без авторизации."""
    response = await client.get(f"api/v1/users/me/books/{shelf_entry.book_id}")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_shelf_router_add_book_to_shelf_happy_path(authenticated_client, book, existing_user):
    """Тест эндпоинта POST /api/v1/users/me/books/{book_id}."""
    response = await authenticated_client.post(
        f"api/v1/users/me/books/{book.id}", json={"status": BookStatus.READ.value}
    )
    assert response.status_code == 201
    assert response.json()["book_id"] == book.id


@pytest.mark.asyncio
async def test_shelf_router_add_book_to_shelf_book_not_found(authenticated_client):
    """Тест эндпоинта POST /api/v1/users/me/books/{book_id} для несуществующей книги."""
    response = await authenticated_client.post("api/v1/users/me/books/99999", json={"status": BookStatus.READ.value})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_shelf_router_add_book_to_shelf_book_already_in_shelf(authenticated_client, shelf_entry):
    """Тест эндпоинта POST /api/v1/users/me/books/{book_id} для книги, уже находящейся на полке."""
    response = await authenticated_client.post(
        f"api/v1/users/me/books/{shelf_entry.book_id}", json={"status": BookStatus.READ.value}
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_shelf_router_add_book_to_shelf_unauthorized(client, book):
    """Тест эндпоинта POST /api/v1/users/me/books/{book_id} без авторизации."""
    response = await client.post(f"api/v1/users/me/books/{book.id}")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_shelf_router_put_shelf_entry_happy_path(authenticated_client, shelf_entry):
    """Тест эндпоинта PUT /api/v1/users/me/books/{book_id}."""
    response = await authenticated_client.put(
        f"api/v1/users/me/books/{shelf_entry.book_id}", json={"status": BookStatus.READ.value, "rating": 10}
    )
    assert response.status_code == 200
    assert response.json()["status"] == BookStatus.READ.value
    assert response.json()["rating"] == 10
    assert response.json()["book_id"] == shelf_entry.book_id


@pytest.mark.asyncio
async def test_shelf_router_put_shelf_entry_book_not_found(authenticated_client):
    """Тест эндпоинта PUT /api/v1/users/me/books/{book_id} для несуществующей книги."""
    response = await authenticated_client.put(
        "api/v1/users/me/books/99999", json={"status": BookStatus.READ.value, "rating": 10}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_shelf_router_put_shelf_entry_book_not_in_shelf(authenticated_client, book_not_in_shelf):
    """Тест эндпоинта PUT /api/v1/users/me/books/{book_id} для книги, не находящейся на полке."""
    response = await authenticated_client.put(
        f"api/v1/users/me/books/{book_not_in_shelf.id}", json={"status": BookStatus.READ.value, "rating": 10}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_shelf_router_put_shelf_entry_unauthorized(client, shelf_entry):
    """Тест эндпоинта PUT /api/v1/users/me/books/{book_id} без авторизации."""
    response = await client.put(
        f"api/v1/users/me/books/{shelf_entry.book_id}", json={"status": BookStatus.READ.value, "rating": 10}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_shelf_router_patch_shelf_entry_happy_path(authenticated_client, shelf_entry):
    """Тест эндпоинта PATCH /api/v1/users/me/books/{book_id}."""
    response = await authenticated_client.patch(
        f"api/v1/users/me/books/{shelf_entry.book_id}", json={"status": BookStatus.READ.value}
    )
    assert response.status_code == 200
    assert response.json()["status"] == BookStatus.READ.value
    assert response.json()["book_id"] == shelf_entry.book_id


@pytest.mark.asyncio
async def test_shelf_router_patch_shelf_entry_book_not_found(authenticated_client):
    """Тест эндпоинта PATCH /api/v1/users/me/books/{book_id} для несуществующей книги."""
    response = await authenticated_client.patch("api/v1/users/me/books/99999", json={"status": BookStatus.READ.value})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_shelf_router_patch_shelf_entry_book_not_in_shelf(authenticated_client, book_not_in_shelf):
    """Тест эндпоинта PATCH /api/v1/users/me/books/{book_id} для книги, не находящейся на полке."""
    response = await authenticated_client.patch(
        f"api/v1/users/me/books/{book_not_in_shelf.id}", json={"status": BookStatus.READ.value}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_shelf_router_patch_shelf_entry_rating_not_allowed(authenticated_client, shelf_entry):
    """Тест эндпоинта PATCH /api/v1/users/me/books/{book_id} для поля rating."""
    response = await authenticated_client.patch(f"api/v1/users/me/books/{shelf_entry.book_id}", json={"rating": 10})
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_shelf_router_patch_shelf_entry_unauthorized(client, shelf_entry):
    """Тест эндпоинта PATCH /api/v1/users/me/books/{book_id} без авторизации."""
    response = await client.patch(
        f"api/v1/users/me/books/{shelf_entry.book_id}", json={"status": BookStatus.READ.value}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_shelf_router_delete_shelf_entry_happy_path(authenticated_client, shelf_entry):
    """Тест эндпоинта DELETE /api/v1/users/me/books/{book_id}."""
    response = await authenticated_client.delete(f"api/v1/users/me/books/{shelf_entry.book_id}")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_shelf_router_delete_shelf_entry_book_not_found(authenticated_client):
    """Тест эндпоинта DELETE /api/v1/users/me/books/{book_id} для несуществующей книги."""
    response = await authenticated_client.delete("api/v1/users/me/books/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_shelf_router_delete_shelf_entry_book_not_in_shelf(authenticated_client, book_not_in_shelf):
    """Тест эндпоинта DELETE /api/v1/users/me/books/{book_id} для книги, не находящейся на полке."""
    response = await authenticated_client.delete(f"api/v1/users/me/books/{book_not_in_shelf.id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_shelf_router_delete_shelf_entry_unauthorized(client, shelf_entry):
    """Тест эндпоинта DELETE /api/v1/users/me/books/{book_id} без авторизации."""
    response = await client.delete(f"api/v1/users/me/books/{shelf_entry.book_id}")
    assert response.status_code == 401
