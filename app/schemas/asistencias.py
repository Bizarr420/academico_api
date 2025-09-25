# app/schemas/asistencias.py
from pydantic import BaseModel, ConfigDict
from datetime import date

class AsistenciaBase(BaseModel):
    fecha: date
    asignacion_id: int
    estudiante_id: int
    estado: str
    observacion: str | None = None

class AsistenciaCreate(AsistenciaBase):
    pass

class AsistenciaOut(AsistenciaBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Para registro masivo
class AsistenciaItem(BaseModel):
    estudiante_id: int
    estado: str
    observacion: str | None = None

class AsistenciaMasivaIn(BaseModel):
    fecha: date
    asignacion_id: int
    items: list[AsistenciaItem]
