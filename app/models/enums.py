import enum


class BookStatus(enum.Enum):
    PLANNED = "в планах"
    READING = "чтение"
    READ = "прочитано"
    ABANDONED = "брошено"
