from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from typing import List
from app.api.deps import get_db
from app.api.deps_extra import require_view
from app.db.models import Nota, Evaluacion, Estudiante, Matricula, Usuario
from app.schemas.notas import NotaCreate, NotaOut

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


from pydantic import BaseModel, Field, conlist


class NotaUpdate(BaseModel):
    calificacion: float = Field(ge=0, le=100)

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
    db.commit(); db.refresh(n)
    return n

# app/api/v1/notas.py
from pydantic import BaseModel, Field, conlist
class NotaItem(BaseModel):
    evaluacion_id: int
    estudiante_id: int
    calificacion: float
class NotaMasivaIn(BaseModel):
    items: list[NotaItem] = Field(min_length=1)

@router.post("/bulk", response_model=List[NotaOut])
def crear_notas_masivo(
    payload: NotaMasivaIn,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("NOTAS")),
):
    out: list[Nota] = []

    for item in payload.items:
        # validaciones básicas
        if not db.get(Evaluacion, item.evaluacion_id):
            raise HTTPException(404, f"Evaluación {item.evaluacion_id} no encontrada")

        if not db.get(Estudiante, item.estudiante_id):
            raise HTTPException(404, f"Estudiante {item.estudiante_id} no encontrado")

        # chequeo de matrícula (según lo agregaste)
        eval_ = db.get(Evaluacion, item.evaluacion_id)
        asig_id = eval_.asignacion_id
        exists = db.execute(
            select(Matricula.id).where(
                Matricula.asignacion_id == asig_id,
                Matricula.estudiante_id == item.estudiante_id,
            )
        ).scalar_one_or_none()
        if not exists:
            raise HTTPException(400, f"El estudiante {item.estudiante_id} no está matriculado en la asignación {asig_id}")

        # evitar duplicados
        dup = db.query(Nota).filter(
            Nota.evaluacion_id == item.evaluacion_id,
            Nota.estudiante_id == item.estudiante_id
        ).first()
        if dup:
            raise HTTPException(400, f"La nota ya existe para estudiante {item.estudiante_id} en evaluación {item.evaluacion_id}")

        out.append(Nota(
            evaluacion_id=item.evaluacion_id,
            estudiante_id=item.estudiante_id,
            calificacion=item.calificacion
        ))

    db.add_all(out)
    db.commit()
    for n in out:
        db.refresh(n)
    return out
