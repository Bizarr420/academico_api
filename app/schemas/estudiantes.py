from pydantic import BaseModel, Field
from pydantic import BaseModel, ConfigDict, Field  # 👈 añade esto

class EstudianteBase(BaseModel):
    persona_id: int = Field(..., gt=0)
    codigo_est: str = Field(..., min_length=1, max_length=50)

class EstudianteCreate(EstudianteBase):
    pass

class EstudianteOut(BaseModel):
    id: int
    persona_id: int
    codigo_est: str

    class Config:
        from_attributes = True
