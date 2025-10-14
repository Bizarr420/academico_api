from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from typing import List
from app.api.deps import get_db
from app.api.deps_extra import require_view
from app.db.models import Nota, Evaluacion, Estudiante, Matricula, Usuario
from app.schemas.notas import (
    NotaBulkError,
    NotaBulkIn,
    NotaBulkSummary,
    NotaCreate,
    NotaOut,
)

router = APIRouter()

@router.post("/", response_model=NotaOut)
def crear_nota(
    data: NotaCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("NOTAS")),
):
    # 1) Validaciones básicas
    eval_ = db.get(Evaluacion, data.evaluacion_id)
    if not eval_:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")

    if not db.get(Estudiante, data.estudiante_id):
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    # 2) Evitar duplicado de nota
    if db.query(Nota).filter(
        Nota.evaluacion_id == data.evaluacion_id,
        Nota.estudiante_id == data.estudiante_id
    ).first():
        raise HTTPException(status_code=400, detail="La nota ya existe para ese estudiante en esa evaluación")

    # 3) ✅ Validar que el estudiante esté matriculado en la asignación de esa evaluación
    asig_id = eval_.asignacion_id
    esta_matriculado = db.execute(
        select(Matricula.id).where(
            Matricula.asignacion_id == asig_id,
            Matricula.estudiante_id == data.estudiante_id,
        )
    ).scalar_one_or_none()

    if not esta_matriculado:
        raise HTTPException(
            status_code=400,
            detail="El estudiante no está matriculado en esta asignación",
        )

    # 4) Crear la nota
    n = Nota(**data.model_dump())
    db.add(n)
    db.commit()
    db.refresh(n)
    return n


@router.get("/evaluacion/{evaluacion_id}", response_model=List[NotaOut])
def notas_de_evaluacion(
    evaluacion_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("NOTAS")),
):
    if not db.get(Evaluacion, evaluacion_id):
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")
    return db.query(Nota).where(Nota.evaluacion_id == evaluacion_id).order_by(Nota.estudiante_id.asc()).all()

@router.get("/promedio-simple")
def promedio_simple(
    estudiante_id: int = Query(..., gt=0),
    asignacion_id: int = Query(..., gt=0),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("NOTAS")),
):
    avg_val = db.query(func.avg(Nota.calificacion)).join(Evaluacion, Nota.evaluacion_id == Evaluacion.id).filter(
        Nota.estudiante_id == estudiante_id,
        Evaluacion.asignacion_id == asignacion_id
    ).scalar()
    return {"estudiante_id": estudiante_id, "asignacion_id": asignacion_id, "promedio_simple": float(avg_val or 0.0)}

@router.get("/promedio-ponderado")
def promedio_ponderado(
    estudiante_id: int = Query(..., gt=0),
    asignacion_id: int = Query(..., gt=0),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("NOTAS")),
):
    sum_prod, sum_pond = db.query(
        func.coalesce(func.sum(Nota.calificacion * Evaluacion.ponderacion), 0.0),
        func.coalesce(func.sum(Evaluacion.ponderacion), 0.0)
    ).join(Evaluacion, Nota.evaluacion_id == Evaluacion.id).filter(
        Nota.estudiante_id == estudiante_id,
        Evaluacion.asignacion_id == asignacion_id
    ).first()
    if not sum_pond or float(sum_pond) == 0.0:
        return {"estudiante_id": estudiante_id, "asignacion_id": asignacion_id, "promedio_ponderado": 0.0, "detalle": "Sin ponderaciones registradas"}
    return {"estudiante_id": estudiante_id, "asignacion_id": asignacion_id, "promedio_ponderado": float(sum_prod)/float(sum_pond)}


from pydantic import BaseModel, Field


class NotaUpdate(BaseModel):
    calificacion: float = Field(ge=0, le=100)
    observacion: str | None = None


@router.put("/{nota_id}", response_model=NotaOut)
def actualizar_nota(
    nota_id: int,
    body: NotaUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("NOTAS")),
):
    n = db.get(Nota, nota_id)
    if not n:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    n.calificacion = body.calificacion
    if body.observacion is not None:
        n.observacion = body.observacion
    db.commit()
    db.refresh(n)
    return n


@router.post("/bulk", response_model=NotaBulkSummary)
def crear_notas_masivo(
    payload: NotaBulkIn,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("NOTAS")),
):
    inserted = 0
    updated = 0
    errors: list[NotaBulkError] = []
    nuevas: list[Nota] = []

    eval_cache: dict[int, Evaluacion | None] = {}
    estudiante_cache: dict[int, Estudiante | None] = {}
    matricula_cache: dict[tuple[int, int], bool] = {}

    for idx, item in enumerate(payload.items):
        evaluacion = eval_cache.get(item.evaluacion_id)
        if evaluacion is None:
            evaluacion = db.get(Evaluacion, item.evaluacion_id)
            eval_cache[item.evaluacion_id] = evaluacion
        if evaluacion is None:
            errors.append(
                NotaBulkError(
                    index=idx,
                    evaluacion_id=item.evaluacion_id,
                    estudiante_id=item.estudiante_id,
                    error="evaluacion_no_encontrada",
                    detalle=f"Evaluación {item.evaluacion_id} no encontrada",
                )
            )
            continue

        estudiante = estudiante_cache.get(item.estudiante_id)
        if estudiante is None:
            estudiante = db.get(Estudiante, item.estudiante_id)
            estudiante_cache[item.estudiante_id] = estudiante
        if estudiante is None:
            errors.append(
                NotaBulkError(
                    index=idx,
                    evaluacion_id=item.evaluacion_id,
                    estudiante_id=item.estudiante_id,
                    error="estudiante_no_encontrado",
                    detalle=f"Estudiante {item.estudiante_id} no encontrado",
                )
            )
            continue

        key = (evaluacion.asignacion_id, item.estudiante_id)
        matriculado = matricula_cache.get(key)
        if matriculado is None:
            matriculado = (
                db.execute(
                    select(Matricula.id).where(
                        Matricula.asignacion_id == evaluacion.asignacion_id,
                        Matricula.estudiante_id == item.estudiante_id,
                    )
                ).scalar_one_or_none()
                is not None
            )
            matricula_cache[key] = matriculado
        if not matriculado:
            errors.append(
                NotaBulkError(
                    index=idx,
                    evaluacion_id=item.evaluacion_id,
                    estudiante_id=item.estudiante_id,
                    error="no_matriculado",
                    detalle=(
                        "El estudiante no está matriculado en la asignación "
                        f"{evaluacion.asignacion_id}"
                    ),
                )
            )
            continue

        existente = (
            db.query(Nota)
            .filter(
                Nota.evaluacion_id == item.evaluacion_id,
                Nota.estudiante_id == item.estudiante_id,
            )
            .one_or_none()
        )

        if existente:
            existente.calificacion = item.calificacion
            existente.observacion = item.observacion
            updated += 1
            continue

        nuevas.append(
            Nota(
                evaluacion_id=item.evaluacion_id,
                estudiante_id=item.estudiante_id,
                calificacion=item.calificacion,
                observacion=item.observacion,
            )
        )
        inserted += 1

    if nuevas:
        db.add_all(nuevas)

    if inserted or updated:
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        else:
            for nota in nuevas:
                db.refresh(nota)

    return NotaBulkSummary(inserted=inserted, updated=updated, errors=errors)
