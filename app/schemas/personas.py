from pydantic import BaseModel, Field
from pydantic.config import ConfigDict
from datetime import date
from typing import Literal

Sexo = Literal["M","F","X"]

class PersonaBase(BaseModel):
    nombres: str = Field(min_length=1, max_length=120)
    apellidos: str = Field(min_length=1, max_length=120)
    sexo: Sexo
    fecha_nacimiento: date
    celular: str | None = None
    direccion: str | None = None

class PersonaCreate(PersonaBase):
    ci_numero: str | None = None
    ci_complemento: str | None = None
    ci_expedicion: str | None = None

class PersonaOut(PersonaBase):
    id: int

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
