# app/api/v1/evaluaciones.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List

from app.api.deps import get_db
from app.api.deps_extra import require_view
from app.db.models import AsignacionDocente, Evaluacion, Usuario
from app.schemas.evaluaciones import EvaluacionCreate, EvaluacionOut

router = APIRouter()  # sin prefix aquí

@router.post("/", response_model=EvaluacionOut)
def crear_evaluacion(
    data: EvaluacionCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("EVALUACIONES")),
):
    # validar FK asignacion
    asig = db.get(AsignacionDocente, data.asignacion_id)
    if not asig:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    if getattr(asig, "estado", "ACTIVO") != "ACTIVO":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "asignacion_inactiva",
                "mensaje": "La asignación está inactiva",
                "asignacion_id": asig.id,
            },
        )

    ev = Evaluacion(
        asignacion_id=data.asignacion_id,
        titulo=data.titulo,
        tipo=data.tipo,
        fecha=data.fecha,
        ponderacion=data.ponderacion,
    )

    try:
        db.add(ev)
        db.commit()
        db.refresh(ev)
        return ev
    except IntegrityError as e:
        db.rollback()
        msg = str(getattr(e, "orig", e))
        if "uq_eval" in msg or "uq_eval_asig_titulo" in msg:
            raise HTTPException(status_code=400, detail="Ya existe una evaluación con ese título en la asignación")
        raise HTTPException(status_code=400, detail="Violación de integridad")

@router.get("/", response_model=List[EvaluacionOut])
def listar_evaluaciones(
    asignacion_id: Optional[int] = Query(default=None, gt=0),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("EVALUACIONES")),
):
    q = db.query(Evaluacion)
    if asignacion_id:
        q = q.filter(Evaluacion.asignacion_id == asignacion_id)
    return q.order_by(Evaluacion.fecha.desc(), Evaluacion.id.desc()).all()

@router.get("/{eval_id}", response_model=EvaluacionOut)
def obtener_evaluacion(
    eval_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("EVALUACIONES")),
):
    ev = db.get(Evaluacion, eval_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")
    return ev
