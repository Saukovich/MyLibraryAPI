from pydantic import BaseModel, ConfigDict, Field, model_validator


class AuthorBase(BaseModel):
    """Базовая модель автора."""

    model_config = ConfigDict(from_attributes=True)

    fullname: str = Field(..., min_length=1, max_length=100)
    birth_year: int = Field(..., ge=0)
    death_year: int | None = Field(None, ge=0)

    @model_validator(mode="after")
    def validate_years(self):
        """Валидация года рождения и смерти."""
        if self.death_year is not None and self.death_year < self.birth_year:
            raise ValueError("Год смерти должен быть больше года рождения.")
        return self


class AuthorResponse(AuthorBase):
    """Модель автора для ответа."""

    id: int


class AuthorCreate(AuthorBase):
    """Модель автора для создания."""

    pass


class AuthorUpdate(AuthorBase):
    """Модель автора для обновления."""

    fullname: str | None = Field(None, min_length=1, max_length=100)
    birth_year: int | None = Field(None, ge=0)
    death_year: int | None = Field(None, ge=0)

    @model_validator(mode="after")
    def validate_years(self):
        """Валидация года рождения и смерти."""
        if self.death_year is not None and self.birth_year is not None and self.death_year < self.birth_year:
            raise ValueError("Год смерти должен быть больше года рождения.")
        return self


class ExistingAuthorRef(BaseModel):
    """Ссылка на существующего автора."""

    id: int = Field(..., gt=0)


NewAuthorRef = AuthorCreate

AuthorRef = ExistingAuthorRef | NewAuthorRef  # Тип для ссылки на автора
