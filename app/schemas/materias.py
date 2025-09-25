from pydantic import BaseModel, ConfigDict, constr
from typing import Optional

class MateriaBase(BaseModel):
    nombre: constr(min_length=2, max_length=100)
    codigo: constr(min_length=2, max_length=20)
    descripcion: Optional[str] = None
    area: Optional[str] = None  # 👈

class MateriaCreate(MateriaBase):
    pass

class MateriaUpdate(BaseModel):
    nombre: Optional[constr(min_length=2, max_length=100)] = None
    codigo: Optional[constr(min_length=2, max_length=20)] = None
    descripcion: Optional[str] = None
    area: Optional[str] = None  # 👈

class MateriaOut(MateriaBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
