# app/schemas/paralelos.py
from pydantic import BaseModel, ConfigDict

class ParaleloBase(BaseModel):
    curso_id: int
    nombre: str
    etiqueta: str

class ParaleloCreate(ParaleloBase): pass

class ParaleloOut(ParaleloBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
