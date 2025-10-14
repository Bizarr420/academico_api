from pydantic import BaseModel, Field


class NotaBulkItem(BaseModel):
    evaluacion_id: int
    estudiante_id: int
    calificacion: float = Field(ge=0, le=100)
    observacion: str | None = None


class NotaBulkError(BaseModel):
    index: int
    evaluacion_id: int | None = None
    estudiante_id: int | None = None
    error: str
    detalle: str


class NotaBulkIn(BaseModel):
    items: list[NotaBulkItem] = Field(min_length=1)


class NotaBulkSummary(BaseModel):
    inserted: int
    updated: int
    errors: list[NotaBulkError]

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
