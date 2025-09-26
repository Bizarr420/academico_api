from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.deps_extra import require_role
from app.db.models import Curso, Materia, PlanCursoMateria
from app.schemas.planes import (
    PlanCursoMateriaCreate,
    PlanCursoMateriaOut,
    PlanCursoMateriaUpdate,
)

router = APIRouter(tags=["planes"])


@router.get("/", response_model=List[PlanCursoMateriaOut])
def listar_planes(
    db: Session = Depends(get_db),
    curso_id: int | None = Query(None, ge=1),
    materia_id: int | None = Query(None, ge=1),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    q = db.query(PlanCursoMateria)
    if curso_id is not None:
        q = q.filter(PlanCursoMateria.curso_id == curso_id)
    if materia_id is not None:
        q = q.filter(PlanCursoMateria.materia_id == materia_id)
    return q.order_by(PlanCursoMateria.id).offset(offset).limit(limit).all()


@router.post(
    "/",
    response_model=PlanCursoMateriaOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin"))],
)
def crear_plan(payload: PlanCursoMateriaCreate, db: Session = Depends(get_db)):
    if not db.get(Curso, payload.curso_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso no encontrado")
    if not db.get(Materia, payload.materia_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Materia no encontrada")

    existente = (
        db.query(PlanCursoMateria)
        .filter(
            PlanCursoMateria.curso_id == payload.curso_id,
            PlanCursoMateria.materia_id == payload.materia_id,
        )
        .first()
    )
    if existente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Plan ya existe")

    plan = PlanCursoMateria(**payload.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.patch(
    "/{plan_id}",
    response_model=PlanCursoMateriaOut,
    dependencies=[Depends(require_role("admin"))],
)
def actualizar_plan(plan_id: int, payload: PlanCursoMateriaUpdate, db: Session = Depends(get_db)):
    plan = db.get(PlanCursoMateria, plan_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan no encontrado")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(plan, key, value)

    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan
