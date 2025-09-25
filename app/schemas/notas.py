from pydantic import BaseModel, Field

class NotaCreate(BaseModel):
    evaluacion_id: int
    estudiante_id: int
    calificacion: float = Field(ge=0, le=100)
    observacion: str | None = None

class NotaOut(BaseModel):
    id: int
    evaluacion_id: int
    estudiante_id: int
    calificacion: float
    observacion: str | None
    class Config:
        from_attributes = True
