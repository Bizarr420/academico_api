from typing import Literal

from pydantic import BaseModel, Field


class PlanCursoMateriaBase(BaseModel):
    curso_id: int = Field(gt=0)
    materia_id: int = Field(gt=0)
    horas_sem: int | None = Field(default=None, ge=0)
    estado: Literal["ACTIVO", "INACTIVO"] = "ACTIVO"


class PlanCursoMateriaCreate(PlanCursoMateriaBase):
    pass


class PlanCursoMateriaUpdate(BaseModel):
    horas_sem: int | None = Field(default=None, ge=0)
    estado: Literal["ACTIVO", "INACTIVO"] | None = None


class PlanCursoMateriaOut(PlanCursoMateriaBase):
    id: int

    class Config:
        from_attributes = True
