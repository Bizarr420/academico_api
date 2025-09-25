# app/schemas/cursos.py
from pydantic import BaseModel, ConfigDict

class CursoBase(BaseModel):
    nivel_id: int
    nombre: str
    etiqueta: str

class CursoCreate(CursoBase): pass

class CursoOut(CursoBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
