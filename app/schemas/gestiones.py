from datetime import date
from pydantic import BaseModel, Field


class GestionBase(BaseModel):
    nombre: str = Field(min_length=1, max_length=20)
    fecha_inicio: date
    fecha_fin: date
    activo: int = Field(default=1, ge=0, le=1)


class GestionCreate(GestionBase):
    pass


class GestionUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=20)
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    activo: int | None = Field(default=None, ge=0, le=1)


class GestionOut(GestionBase):
    id: int

    class Config:
        from_attributes = True
