"""Pydantic schemas for asignaciones (teaching assignments)."""

from pydantic import BaseModel, ConfigDict, Field


class AsignacionBase(BaseModel):
    gestion_id: int = Field(gt=0)
    docente_id: int = Field(gt=0)
    materia_id: int = Field(gt=0)
    curso_id: int = Field(gt=0)
    paralelo_id: int = Field(gt=0)


class AsignacionCreate(AsignacionBase):
    pass


class AsignacionOut(AsignacionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
