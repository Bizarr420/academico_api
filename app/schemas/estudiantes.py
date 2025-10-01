from __future__ import annotations

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

    @model_validator(mode="before")
    @classmethod
    def _normalise_anio_ingreso(cls, data: "EstudianteOut" | dict) -> "EstudianteOut" | dict:
        """Ensure ``anio_ingreso`` values falling outside the accepted range are nulled.

        Legacy datasets may contain ``0`` or other out-of-bounds values for the
        ``anio_ingreso`` column. Those values trigger FastAPI's response model
        validation because the schema restricts the field to ``[1900, año actual + 1]``.
        To avoid returning a 500 error we coerce those legacy values to ``None``
        before field validation runs.
        """

        def _sanitise(value):
            if value is None:
                return None
            try:
                year = int(value)
            except (TypeError, ValueError):
                return value

            max_year = date.today().year + 1
            return year if 1900 <= year <= max_year else None

        if isinstance(data, dict):
            raw_year = data.get("anio_ingreso")
            normalised = _sanitise(raw_year)
            if normalised != raw_year:
                data = dict(data)
                data["anio_ingreso"] = normalised
            return data

        raw_year = getattr(data, "anio_ingreso", None)
        normalised = _sanitise(raw_year)
        if normalised == raw_year:
            return data

        coerced = {
            field_name: getattr(data, field_name, None)
            for field_name in cls.model_fields
        }
        coerced["anio_ingreso"] = normalised
        return coerced

    model_config = ConfigDict(from_attributes=True)
