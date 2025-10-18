# app/schemas/paralelos.py
from typing import Literal

from pydantic import BaseModel, ConfigDict


class ParaleloBase(BaseModel):
    curso_id: int
    nombre: str
    estado: Literal["ACTIVO", "INACTIVO"] = "ACTIVO"

class ParaleloCreate(ParaleloBase): pass

class ParaleloOut(ParaleloBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
