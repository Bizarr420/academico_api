from datetime import date
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field

TipoEval = Literal["EXAMEN", "TAREA", "PROYECTO", "PRACTICA", "OTRO"]

class EvaluacionBase(BaseModel):
    asignacion_id: int = Field(gt=0)
    titulo: str = Field(min_length=1, max_length=120)
    tipo: TipoEval = "OTRO"
    fecha: date
    ponderacion: Decimal = Field(ge=0, le=100)

class EvaluacionCreate(BaseModel):
    asignacion_id: int
    titulo: str = Field(min_length=1, max_length=120)
    tipo: TipoEval = "OTRO"
    fecha: date
    ponderacion: float = Field(ge=0, le=100)

class EvaluacionOut(BaseModel):
    id: int
    asignacion_id: int
    titulo: str
    tipo: TipoEval
    fecha: date
    ponderacion: float
    class Config:
        from_attributes = True
