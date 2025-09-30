from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, constr

class MateriaBase(BaseModel):
    nombre: constr(min_length=2, max_length=100)
    codigo: constr(min_length=2, max_length=20)
    descripcion: Optional[str] = None
    area: Optional[str] = None
    estado: Literal["ACTIVO", "INACTIVO"] = "ACTIVO"

class MateriaCreate(MateriaBase):
    pass

class MateriaUpdate(BaseModel):
    nombre: Optional[constr(min_length=2, max_length=100)] = None
    codigo: Optional[constr(min_length=2, max_length=20)] = None
    descripcion: Optional[str] = None
    area: Optional[str] = None
    estado: Optional[Literal["ACTIVO", "INACTIVO"]] = None

class MateriaOut(MateriaBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
