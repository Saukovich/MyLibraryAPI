import pytest


@pytest.mark.asyncio
async def test_notes_router_get_notes(authenticated_client, book, existing_user, note):
    """Тест эндпоинта GET /api/v1/users/me/books/{book_id}/notes/."""
    response = await authenticated_client.get(f"api/v1/users/me/books/{book.id}/notes/")
    assert response.status_code == 200
    assert response.json()[0]["id"] == note.id
    assert response.json()[0]["text"] == note.text
    assert response.json()[0]["page"] == note.page


@pytest.mark.asyncio
async def test_notes_router_get_notes_book_not_found(authenticated_client, existing_user):
    """Тест эндпоинта GET /api/v1/users/me/books/{book_id}/notes/ с несуществующей книгой."""
    response = await authenticated_client.get("api/v1/users/me/books/99999/notes/")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_notes_router_get_notes_unauthorized(client, book, existing_user):
    """Тест эндпоинта GET /api/v1/users/me/books/{book_id}/notes/ без авторизации."""
    response = await client.get(f"api/v1/users/me/books/{book.id}/notes/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_notes_router_get_note_happy_path(authenticated_client, book, existing_user, note):
    """Тест эндпоинта GET /api/v1/users/me/books/{book_id}/notes/{note_id}."""
    response = await authenticated_client.get(f"api/v1/users/me/books/{book.id}/notes/{note.id}")
    assert response.status_code == 200
    assert response.json()["id"] == note.id
    assert response.json()["text"] == note.text
    assert response.json()["page"] == note.page


@pytest.mark.asyncio
async def test_notes_router_get_note_book_not_found(authenticated_client, existing_user, note):
    """Тест эндпоинта GET /api/v1/users/me/books/{book_id}/notes/{note_id} с несуществующей книгой."""
    response = await authenticated_client.get(f"api/v1/users/me/books/99999/notes/{note.id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_notes_router_get_note_note_not_found(authenticated_client, book, existing_user):
    """Тест эндпоинта GET /api/v1/users/me/books/{book_id}/notes/{note_id} с несуществующим заметкой."""
    response = await authenticated_client.get(f"api/v1/users/me/books/{book.id}/notes/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_notes_router_get_note_unauthorized(client, book, existing_user, note):
    """Тест эндпоинта GET /api/v1/users/me/books/{book_id}/notes/{note_id} без авторизации."""
    response = await client.get(f"api/v1/users/me/books/{book.id}/notes/{note.id}")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_notes_router_create_note_happy_path(authenticated_client, book, existing_user, shelf_entry):
    """Тест эндпоинта POST /api/v1/users/me/books/{book_id}/notes/."""
    response = await authenticated_client.post(
        f"api/v1/users/me/books/{book.id}/notes/", json={"text": "Test Note", "page": 1}
    )
    assert response.status_code == 201
    assert response.json()["text"] == "Test Note"
    assert response.json()["page"] == 1


@pytest.mark.asyncio
async def test_notes_router_create_note_book_not_found(authenticated_client, existing_user):
    """Тест эндпоинта POST /api/v1/users/me/books/{book_id}/notes/ с несуществующей книгой."""
    response = await authenticated_client.post(
        "api/v1/users/me/books/99999/notes/", json={"text": "Test Note", "page": 1}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_notes_router_create_note_unauthorized(client, book, existing_user):
    """Тест эндпоинта POST /api/v1/users/me/books/{book_id}/notes/ без авторизации."""
    response = await client.post(f"api/v1/users/me/books/{book.id}/notes/", json={"text": "Test Note", "page": 1})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_notes_router_put_note_happy_path(authenticated_client, book, existing_user, note):
    """Тест эндпоинта PUT /api/v1/users/me/books/{book_id}/notes/{note_id}."""
    response = await authenticated_client.put(
        f"api/v1/users/me/books/{book.id}/notes/{note.id}", json={"text": "Updated Note", "page": 2}
    )
    assert response.status_code == 200
    assert response.json()["text"] == "Updated Note"
    assert response.json()["page"] == 2


@pytest.mark.asyncio
async def test_notes_router_put_note_book_not_found(authenticated_client, existing_user, note):
    """Тест эндпоинта PUT /api/v1/users/me/books/{book_id}/notes/{note_id} с несуществующей книгой."""
    response = await authenticated_client.put(
        f"api/v1/users/me/books/99999/notes/{note.id}", json={"text": "Updated Note", "page": 2}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_notes_router_put_note_note_not_found(authenticated_client, book, existing_user):
    """Тест эндпоинта PUT /api/v1/users/me/books/{book_id}/notes/{note_id} с несуществующим заметкой."""
    response = await authenticated_client.put(
        f"api/v1/users/me/books/{book.id}/notes/99999", json={"text": "Updated Note", "page": 2}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_notes_router_put_note_unauthorized(client, book, existing_user, note):
    """Тест эндпоинта PUT /api/v1/users/me/books/{book_id}/notes/{note_id} без авторизации."""
    response = await client.put(
        f"api/v1/users/me/books/{book.id}/notes/{note.id}", json={"text": "Updated Note", "page": 2}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_notes_router_patch_note_happy_path(authenticated_client, book, existing_user, note):
    """Тест эндпоинта PATCH /api/v1/users/me/books/{book_id}/notes/{note_id}."""
    response = await authenticated_client.patch(
        f"api/v1/users/me/books/{book.id}/notes/{note.id}", json={"text": "Updated Note"}
    )
    assert response.status_code == 200
    assert response.json()["text"] == "Updated Note"
    assert response.json()["page"] == note.page


@pytest.mark.asyncio
async def test_notes_router_patch_note_book_not_found(authenticated_client, existing_user, note):
    """Тест эндпоинта PATCH /api/v1/users/me/books/{book_id}/notes/{note_id} с несуществующей книгой."""
    response = await authenticated_client.patch(
        f"api/v1/users/me/books/99999/notes/{note.id}", json={"text": "Updated Note"}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_notes_router_patch_note_note_not_found(authenticated_client, book, existing_user):
    """Тест эндпоинта PATCH /api/v1/users/me/books/{book_id}/notes/{note_id} с несуществующим заметкой."""
    response = await authenticated_client.patch(
        f"api/v1/users/me/books/{book.id}/notes/99999", json={"text": "Updated Note"}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_notes_router_patch_note_unauthorized(client, book, existing_user, note):
    """Тест эндпоинта PATCH /api/v1/users/me/books/{book_id}/notes/{note_id} без авторизации."""
    response = await client.patch(f"api/v1/users/me/books/{book.id}/notes/{note.id}", json={"text": "Updated Note"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_notes_router_delete_note_happy_path(authenticated_client, book, existing_user, note):
    """Тест эндпоинта DELETE /api/v1/users/me/books/{book_id}/notes/{note_id}."""
    response = await authenticated_client.delete(f"api/v1/users/me/books/{book.id}/notes/{note.id}")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_notes_router_delete_note_book_not_found(authenticated_client, existing_user, note):
    """Тест эндпоинта DELETE /api/v1/users/me/books/{book_id}/notes/{note_id} с несуществующей книгой."""
    response = await authenticated_client.delete(f"api/v1/users/me/books/99999/notes/{note.id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_notes_router_delete_note_note_not_found(authenticated_client, book, existing_user):
    """Тест эндпоинта DELETE /api/v1/users/me/books/{book_id}/notes/{note_id} с несуществующим заметкой."""
    response = await authenticated_client.delete(f"api/v1/users/me/books/{book.id}/notes/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_notes_router_delete_note_unauthorized(client, book, existing_user, note):
    """Тест эндпоинта DELETE /api/v1/users/me/books/{book_id}/notes/{note_id} без авторизации."""
    response = await client.delete(f"api/v1/users/me/books/{book.id}/notes/{note.id}")
    assert response.status_code == 401
