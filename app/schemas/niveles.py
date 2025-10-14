from typing import Literal

from pydantic import BaseModel, Field


class NivelBase(BaseModel):
    nombre: str = Field(min_length=1, max_length=50)
    etiqueta: str = Field(min_length=1, max_length=20)
    estado: Literal["ACTIVO", "INACTIVO"] = "ACTIVO"


class NivelCreate(NivelBase):
    pass


class NivelUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=50)
    etiqueta: str | None = Field(default=None, min_length=1, max_length=20)
    estado: Literal["ACTIVO", "INACTIVO"] | None = None


class NivelOut(NivelBase):
    id: int

    class Config:
        from_attributes = True
