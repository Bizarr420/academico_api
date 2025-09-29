from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.deps_extra import require_view
from app.db.models import Nota, Evaluacion, Usuario

router = APIRouter(tags=["reportes"])

@router.get("/estudiante/{est_id}/notas")
def notas_estudiante(
    est_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("REPORTES")),
):
    q = (
        db.query(
            Evaluacion.titulo,
            Evaluacion.fecha,
            Nota.calificacion,
            Evaluacion.asignacion_id
        )
        .join(Nota, Nota.evaluacion_id == Evaluacion.id)
        .filter(Nota.estudiante_id == est_id)
        .order_by(Evaluacion.fecha.asc(), Evaluacion.id.asc())
    )
    return [
        {
            "titulo": t,
            "fecha": f.isoformat() if isinstance(f, date) else str(f),
            "calificacion": float(c),
            "asignacion_id": int(a),
        }
        for (t, f, c, a) in q
    ]

@router.get("/curso/{asig_id}/promedios")
def promedios_curso(
    asig_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("REPORTES")),
):
    q = (
        db.query(
            Nota.estudiante_id,
            func.avg(Nota.calificacion)
        )
        .join(Evaluacion, Nota.evaluacion_id == Evaluacion.id)
        .filter(Evaluacion.asignacion_id == asig_id)
        .group_by(Nota.estudiante_id)
        .order_by(Nota.estudiante_id.asc())
    )
    return [{"estudiante_id": int(e), "promedio": float(p)} for (e, p) in q]
