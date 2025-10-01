from enum import Enum
from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.personas import PersonaCreate, PersonaOut


class SituacionEstudianteEnum(str, Enum):
    REGULAR = "REGULAR"
    RETIRADO = "RETIRADO"
    EGRESADO = "EGRESADO"
    CONDICIONAL = "CONDICIONAL"


class EstadoEstudianteEnum(str, Enum):
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"


class EstudianteBase(BaseModel):
    codigo_rude: str = Field(..., min_length=1, max_length=50)
    anio_ingreso: int | None = Field(
        default=None,
        ge=1900,
        le=date.today().year + 1,
        description="Año de ingreso al establecimiento",
    )
    situacion: SituacionEstudianteEnum = SituacionEstudianteEnum.REGULAR
    estado: EstadoEstudianteEnum = EstadoEstudianteEnum.ACTIVO


class EstudianteCreate(EstudianteBase):
    persona_id: int | None = Field(default=None, gt=0)
    persona: PersonaCreate | None = None

    @model_validator(mode="after")
    def check_persona_reference(self) -> "EstudianteCreate":
        persona_id_provided = self.persona_id is not None
        persona_object_provided = self.persona is not None
        if persona_id_provided == persona_object_provided:
            raise ValueError("Debe proporcionar únicamente persona_id o persona")
        return self


class EstudianteOut(EstudianteBase):
    id: int
    persona_id: int
    persona: PersonaOut | None = None

    model_config = ConfigDict(from_attributes=True)
