from pydantic import BaseModel, ConfigDict, Field

class EstudianteBase(BaseModel):
    persona_id: int = Field(..., gt=0)
    codigo_est: str = Field(..., min_length=1, max_length=50)

class EstudianteCreate(EstudianteBase):
    pass

class EstudianteOut(EstudianteBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
