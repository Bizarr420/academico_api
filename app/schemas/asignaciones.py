from pydantic import BaseModel, Field
from pydantic import BaseModel, ConfigDict, Field  # 👈 añade esto

class AsignacionBase(BaseModel):
    docente_id: int
    materia_id: int
    curso_id: int
    paralelo_id: int
    gestion: str = Field(..., max_length=10)

class AsignacionCreate(AsignacionBase):
    pass

class AsignacionOut(AsignacionBase):
    id: int
    class Config:
        from_attributes = True
