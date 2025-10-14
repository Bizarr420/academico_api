# app/schemas/cursos.py
from typing import Literal

from pydantic import BaseModel, ConfigDict


class CursoBase(BaseModel):
    nivel_id: int
    nombre: str
    etiqueta: str
    estado: Literal["ACTIVO", "INACTIVO"] = "ACTIVO"

class CursoCreate(CursoBase): pass

class CursoOut(CursoBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
