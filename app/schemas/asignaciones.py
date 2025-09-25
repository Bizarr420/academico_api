"""Pydantic schemas for asignaciones (teaching assignments)."""

from pydantic import BaseModel, ConfigDict, Field


class AsignacionBase(BaseModel):
    docente_id: int
    materia_id: int
    curso_id: int
    paralelo_id: int
    gestion: str = Field(..., max_length=10)


class AsignacionCreate(AsignacionBase):
    pass


class AsignacionOut(AsignacionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
