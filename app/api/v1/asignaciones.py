from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.deps_extra import require_view
from app.db.models import AsignacionDocente, Docente, Gestion, Materia, Curso, Paralelo, Usuario

router = APIRouter(tags=["asignaciones"])

@router.post("/")
def crear_asignacion(
    data: dict,  # o tu esquema
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("ASIGNACIONES")),
):
    # data: {gestion: "2025", docente_id, materia_id, curso_id, paralelo_id}
    g = db.query(Gestion).filter(Gestion.nombre == data["gestion"]).first()
    if not g: raise HTTPException(404, "Gestión no encontrada")

    if not db.get(Docente, data["docente_id"]):   raise HTTPException(404, "Docente no encontrado")
    if not db.get(Materia, data["materia_id"]):   raise HTTPException(404, "Materia no encontrada")
    if not db.get(Curso, data["curso_id"]):       raise HTTPException(404, "Curso no encontrado")
    if not db.get(Paralelo, data["paralelo_id"]): raise HTTPException(404, "Paralelo no encontrado")

    existente = db.query(AsignacionDocente).filter_by(
        gestion_id=g.id,
        docente_id=data["docente_id"],
        materia_id=data["materia_id"],
        curso_id=data["curso_id"],
        paralelo_id=data["paralelo_id"],
    ).first()
    if existente:
        return existente

    a = AsignacionDocente(
        gestion_id=g.id,
        docente_id=data["docente_id"],
        materia_id=data["materia_id"],
        curso_id=data["curso_id"],
        paralelo_id=data["paralelo_id"],
    )
    db.add(a); db.commit(); db.refresh(a)
    return a

@router.get("/")
def listar_asignaciones(
    gestion: str | None = Query(default=None),
    docente_id: int | None = Query(default=None),
    curso_id: int | None = Query(default=None),
    paralelo_id: int | None = Query(default=None),
    materia_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("ASIGNACIONES")),
):
    q = db.query(AsignacionDocente)
    if gestion is not None:
        q = q.join(Gestion, Gestion.id == AsignacionDocente.gestion_id)\
             .filter(Gestion.nombre == gestion)
    if docente_id is not None:
        q = q.filter(AsignacionDocente.docente_id == docente_id)
    if curso_id is not None:
        q = q.filter(AsignacionDocente.curso_id == curso_id)
    if paralelo_id is not None:
        q = q.filter(AsignacionDocente.paralelo_id == paralelo_id)
    if materia_id is not None:
        q = q.filter(AsignacionDocente.materia_id == materia_id)
    return q.all()
