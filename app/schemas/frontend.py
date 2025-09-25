from pydantic import BaseModel

from app.schemas.personas import PersonaOut


class StudentItem(BaseModel):
    id: int
    persona_id: int
    codigo_est: str
    persona: PersonaOut


class PaginatedStudents(BaseModel):
    items: list[StudentItem]
    total: int
    page: int
    page_size: int


class TeacherItem(BaseModel):
    id: int
    persona_id: int
    titulo: str | None = None
    persona: PersonaOut


class PaginatedTeachers(BaseModel):
    items: list[TeacherItem]
    total: int
    page: int
    page_size: int
