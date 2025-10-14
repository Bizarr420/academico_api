from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class GestionBase(BaseModel):
    nombre: str = Field(min_length=1, max_length=20)
    fecha_inicio: date
    fecha_fin: date
    estado: Literal["ACTIVO", "INACTIVO"] = "ACTIVO"


class GestionCreate(GestionBase):
    pass


class GestionUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=20)
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    estado: Literal["ACTIVO", "INACTIVO"] | None = None


class GestionOut(GestionBase):
    id: int

    class Config:
        from_attributes = True
