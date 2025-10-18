from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.personas import PersonaCreate, PersonaOut

from app.schemas.materias import MateriaOut
from app.schemas.cursos import CursoOut
from pydantic import BaseModel


# Nuevo esquema para la asignación completa
class ParaleloOut(BaseModel):
    id: int
    nombre: str
    etiqueta: str | None = None

    model_config = ConfigDict(from_attributes=True)

class AsignacionDocenteOut(BaseModel):
    id: int
    gestion_id: int
    materia: MateriaOut
    curso: CursoOut
    paralelo: ParaleloOut

    model_config = ConfigDict(from_attributes=True)


class DocenteBase(BaseModel):
    titulo: str | None = Field(default=None, max_length=120)
    profesion: str | None = Field(default=None, max_length=120)
    estado: Literal["ACTIVO", "INACTIVO"] = "ACTIVO"


class DocenteCreate(DocenteBase):
    persona_id: int | None = Field(default=None, gt=0)
    persona: PersonaCreate | None = None
    materia_id: int | None = Field(default=None, gt=0)
    curso_ids: list[int] | None = Field(default=None)

    @model_validator(mode="after")
    def check_persona_reference(self) -> "DocenteCreate":
        persona_id_provided = self.persona_id is not None
        persona_object_provided = self.persona is not None
        if persona_id_provided == persona_object_provided:
            raise ValueError("Debe proporcionar únicamente persona_id o persona")
        return self


class DocenteUpdate(BaseModel):
    titulo: str | None = Field(default=None, max_length=120)
    profesion: str | None = Field(default=None, max_length=120)
    estado: Literal["ACTIVO", "INACTIVO"] | None = None


class DocenteOut(DocenteBase):
    id: int
    persona_id: int
    persona: PersonaOut | None = None
    materias: list[MateriaOut] = []
    cursos: list[CursoOut] = []
    asignaciones: list[AsignacionDocenteOut] = []

    model_config = ConfigDict(from_attributes=True)
