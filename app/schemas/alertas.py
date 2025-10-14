from pydantic import BaseModel, ConfigDict, conint
from typing import Optional
from typing import Literal
from datetime import datetime

class AlertaBase(BaseModel):
    gestion: conint(ge=2000, le=2100)
    asignacion_id: int
    estudiante_id: int
    tipo: str
    motivo: str
    score: Optional[conint(ge=0, le=100)] = None
    estado: str = "NUEVO"
    observacion: str | None = None

class AlertaCreate(AlertaBase): pass

class AlertaOut(BaseModel):
    id: int
    gestion: int
    asignacion_id: int
    estudiante_id: int
    tipo: str
    motivo: str
    score: int | None = None
    estado: Literal["NUEVO","LEIDO","CERRADO"]
    observacion: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)  # 👈 importante

class AlertaUpdate(BaseModel):
    estado: Literal["NUEVO","LEIDO","CERRADO"] | None = None
    observacion: str | None = None
