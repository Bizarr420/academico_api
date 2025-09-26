from datetime import date

from pydantic import BaseModel, Field, field_serializer
from pydantic.config import ConfigDict

from app.db.models import SexoEnum

class PersonaBase(BaseModel):
    nombres: str = Field(min_length=1, max_length=120)
    apellidos: str = Field(min_length=1, max_length=120)
    sexo: SexoEnum
    fecha_nacimiento: date
    celular: str | None = None
    direccion: str | None = None

    @field_serializer("sexo", when_used="json")
    def serialize_sexo(self, sexo: SexoEnum) -> str:
        if isinstance(sexo, SexoEnum):
            return sexo.short_code
        return str(sexo)

class PersonaCreate(PersonaBase):
    ci_numero: str | None = None
    ci_complemento: str | None = None
    ci_expedicion: str | None = None

class PersonaOut(PersonaBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
