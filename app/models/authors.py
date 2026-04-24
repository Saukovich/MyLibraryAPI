from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, validates

from app.core.database import Model


class Author(Model):
    """
    Модель автора

    Attributes:
        id (int): Идентификатор автора.
        fullname (str): Полное имя автора.
        birth_year (int): Год рождения автора.
        death_year (int | None): Год смерти автора (None, если автор жив).
    """

    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    fullname: Mapped[str] = mapped_column(String(100), nullable=False)
    birth_year: Mapped[int] = mapped_column(nullable=False)
    death_year: Mapped[int | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    @validates("fullname")
    def validate_fullname(self, key: str, value: str) -> str:
        """
        Валидация полного имени автора.
        :param key: str - Атрибут, который валидируется
        :param value: str - Полное имя автора
        :return: str - Значение полного имени автора
        """
        if value is None:
            raise ValueError("Fullname is required")
        if len(value) > 100:
            raise ValueError("Fullname is must be less than 100 characters")
        return value

    @validates("birth_year")
    def validate_birth_year(self, key: str, value: int) -> int:
        """
        Валидация года рождения автора.
        :param key: str - Атрибут, который валидируется
        :param value: int - Год рождения автора
        :return: int - Значение года рождения автора
        """
        if value is None:
            raise ValueError("Birth year is required")
        if value <= 0:
            raise ValueError("Birth year must be greater than 0")
        return value

    @validates("death_year")
    def validate_death_year(self, key: str, value: int | None) -> int | None:
        """
        Валидация года смерти автора.
        :param key: str - Атрибут, который валидируется
        :param value: int | None - Год смерти автора
        :return: int | None - Значение года смерти автора
            None - если автор жив
            int - если автор умер
        """
        if value is not None and value <= 0:
            raise ValueError("Death year must be greater than 0 or None")
        return value
