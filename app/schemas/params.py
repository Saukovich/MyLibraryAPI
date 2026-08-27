from pydantic import BaseModel, Field, field_validator, model_validator


class PaginationParams(BaseModel):
    """
    Query-параметры для пагинации.

    Attributes:
        limit (int): Количество возвращаемых элементов (по умолчанию 100).
        offset (int): Смещение для пагинации (по умолчанию 0).
    """

    limit: int = Field(100, ge=1, le=100)
    offset: int = Field(0, ge=0)


class BookFilterParams(PaginationParams):
    """
    Query-параметры для фильтрации книг.

    Attributes:
        author_id (int | None): Фильтрация по ID автора.
        author_name (str | None): Фильтрация по совпадению с именем автора.
        title (str | None): Фильтрация по совпадению с названием книги.
        one_author (bool | None): Фильтрация по наличию только одного автора у книги.
            Если True, то книга должна иметь только одного автора.
            Если False, то книга может иметь больше одного автора.
        release_year_min (int | None): Минимальный год выпуска книги.
        release_year_max (int | None): Максимальный год выпуска книги.
        sort_by (str): Поле для сортировки (по умолчанию 'id').
            Возможные значения: 'id', 'title', 'release_year', 'author_id'.
        order_by (str): Порядок сортировки (по умолчанию 'asc').
            Возможные значения: 'asc' (по возрастанию) или 'desc' (по убыванию).
    """

    author_id: int | None = None
    author_name: str | None = Field(None, min_length=1, max_length=255)
    title: str | None = Field(None, min_length=1, max_length=255)
    one_author: bool | None = False
    release_year_min: int | None = Field(None, ge=1)
    release_year_max: int | None = Field(None, ge=1)
    sort_by: str = "id"
    order_by: str = "asc"

    @field_validator("sort_by", mode="after")
    def validate_sort_by(cls, v):
        """Валидация поля для сортировки.
        Возможные значения: "id", "title", "release_year", "author_id"."""
        if v not in ["id", "title", "release_year", "author_id"]:
            raise ValueError("Недопустимое значение для sort_by")
        return v

    @field_validator("order_by", mode="after")
    def validate_order_by(cls, v):
        """Валидация порядка сортировки.
        Возможные значения: "asc" и "desc"."""
        if v not in ["asc", "desc"]:
            raise ValueError("Недопустимое значение для order_by")
        return v

    @model_validator(mode="after")
    def validate_release_year(self):
        """Валидация диапазона годов выпуска.
        Минимальный год выпуска не может быть больше максимального года выпуска."""
        if self.release_year_min and self.release_year_max:
            if self.release_year_min > self.release_year_max:
                raise ValueError("Минимальный год выпуска не может быть больше максимального года выпуска")
        return self


class AuthorFilterParams(PaginationParams):
    """
    Query-параметры для фильтрации авторов.

    Attributes:
        fullname (str | None): Фильтрация по совпадению с полным именем автора.
        birth_year_min (int | None): Минимальный год рождения автора.
        birth_year_max (int | None): Максимальный год рождения автора.
        is_dead (bool | None): Фильтрация по статусу жизни автора (жив/мертв).
            Если True, то автор должен быть мёртв.
            Если False, то автор должен быть жив.
        death_year_min (int | None): Минимальный год смерти автора.
        death_year_max (int | None): Максимальный год смерти автора.
        sort_by (str): Поле для сортировки (по умолчанию 'id').
            Возможные значения: 'id', 'fullname', 'birth_year', 'death_year'.
        order_by (str): Порядок сортировки (по умолчанию 'asc').
            Возможные значения: 'asc' (по возрастанию) или 'desc' (по убыванию).
    """

    fullname: str | None = Field(None, min_length=1, max_length=255)
    birth_year_min: int | None = Field(None, ge=1)
    birth_year_max: int | None = Field(None, ge=1)
    is_dead: bool | None = None
    death_year_min: int | None = Field(None, ge=1)
    death_year_max: int | None = Field(None, ge=1)
    sort_by: str = "id"
    order_by: str = "asc"

    @field_validator("sort_by", mode="after")
    def validate_sort_by(cls, v):
        """Валидация поля для сортировки.
        Возможные значения: "id", "fullname", "birth_year", "death_year"."""
        if v not in ["id", "fullname", "birth_year", "death_year"]:
            raise ValueError("Недопустимое значение для sort_by")
        return v

    @field_validator("order_by", mode="after")
    def validate_order_by(cls, v):
        """Валидация порядка сортировки.
        Возможные значения: "asc" и "desc"."""
        if v not in ["asc", "desc"]:
            raise ValueError("Недопустимое значение для order_by")
        return v

    @model_validator(mode="after")
    def validate_birth_year(self):
        """Валидация диапазона годов рождения.
        Минимальный год рождения не может быть больше максимального года рождения."""
        if self.birth_year_min and self.birth_year_max:
            if self.birth_year_min > self.birth_year_max:
                raise ValueError("Минимальный год рождения не может быть больше максимального года рождения")
        return self

    @model_validator(mode="after")
    def validate_is_dead(self):
        """Валидация статуса жизни автора.
        Если автор мёртв, то год смерти не должен быть указан."""
        if self.is_dead is not None:
            if not self.is_dead and (self.death_year_min or self.death_year_max):
                raise ValueError("Если автор жив, то год смерти не должен быть указан")
        return self

    @model_validator(mode="after")
    def validate_death_year(self):
        """Валидация диапазона годов смерти.
        Минимальный год смерти не может быть больше максимального года смерти."""
        if self.death_year_min and self.death_year_max:
            if self.death_year_min > self.death_year_max:
                raise ValueError("Минимальный год смерти не может быть больше максимального года смерти")
        return self

    @model_validator(mode="after")
    def validate_combination_birth_death_years(self):
        """Валидация комбинации годов рождения и смерти.
        Год рождения не может быть больше года смерти."""
        if self.birth_year_min and self.death_year_min:
            if self.birth_year_min > self.death_year_min:
                raise ValueError("Минимальный год рождения не может быть больше минимального года смерти")

        if self.birth_year_max and self.death_year_max:
            if self.birth_year_max > self.death_year_max:
                raise ValueError("Максимальный год рождения не может быть больше максимального года смерти")

        if self.birth_year_min and self.death_year_max:
            if self.birth_year_min > self.death_year_max:
                raise ValueError("Минимальный год рождения не может быть больше максимального года смерти")
        return self


class NoteFilterParams(PaginationParams):
    page_min: int | None = Field(None, ge=1)
    page_max: int | None = Field(None, ge=1)
    sort_by: str = "id"
    order_by: str = "asc"

    @field_validator("sort_by", mode="after")
    def validate_sort_by(cls, v):
        """Валидация поля для сортировки.
        Возможные значения: "id", "text", "page", "created_at"."""
        if v not in ["id", "text", "page", "created_at"]:
            raise ValueError("Недопустимое значение для sort_by")
        return v

    @field_validator("order_by", mode="after")
    def validate_order_by(cls, v):
        """Валидация порядка сортировки.
        Возможные значения: "asc" и "desc"."""
        if v not in ["asc", "desc"]:
            raise ValueError("Недопустимое значение для order_by")
        return v

    @model_validator(mode="after")
    def validate_page(self):
        """Валидация диапазона страниц.
        Минимальная страница не может быть больше максимальной страницы."""
        if self.page_min and self.page_max and self.page_min > self.page_max:
            raise ValueError("Минимальная страница не может быть больше максимальной страницы")
        return self
