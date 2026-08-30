from pydantic import BaseModel, ConfigDict, Field


class NoteBase(BaseModel):
    """Базовая схема заметки."""

    model_config = ConfigDict(from_attributes=True)

    text: str = Field(..., min_length=1)
    page: int = Field(..., ge=1)


class NoteResponse(NoteBase):
    """Схема ответа на запрос заметки."""

    id: int


class NoteCreate(NoteBase):
    """Схема создания заметки."""

    pass


class NoteUpdate(NoteBase):
    """Схема обновления заметки."""

    text: str | None = None
    page: int | None = Field(None, ge=1)
