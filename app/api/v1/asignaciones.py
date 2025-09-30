from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.deps_extra import require_view
from app.db.models import AsignacionDocente, Docente, Gestion, Materia, Curso, Paralelo, Usuario
from app.schemas.asignaciones import AsignacionCreate, AsignacionOut

router = APIRouter(tags=["asignaciones"])

@router.post(
    "/",
    response_model=AsignacionOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_asignacion(
    payload: AsignacionCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("ASIGNACIONES")),
):
    gestion = db.get(Gestion, payload.gestion_id)
    if not gestion:
        raise HTTPException(status_code=404, detail="Gestión no encontrada")

    if not db.get(Docente, payload.docente_id):
        raise HTTPException(status_code=404, detail="Docente no encontrado")
    if not db.get(Materia, payload.materia_id):
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    if not db.get(Curso, payload.curso_id):
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    if not db.get(Paralelo, payload.paralelo_id):
        raise HTTPException(status_code=404, detail="Paralelo no encontrado")

    existe = (
        db.query(AsignacionDocente)
        .filter_by(**payload.model_dump())
        .first()
    )
    if existe:
        raise HTTPException(status_code=409, detail="Asignación ya existe")

    asignacion = AsignacionDocente(**payload.model_dump())
    db.add(asignacion)
    db.commit()
    db.refresh(asignacion)
    return asignacion


@router.get("/", response_model=list[AsignacionOut])
def listar_asignaciones(
    gestion_id: int | None = Query(default=None, gt=0),
    gestion: str | None = Query(default=None),
    docente_id: int | None = Query(default=None, gt=0),
    curso_id: int | None = Query(default=None, gt=0),
    paralelo_id: int | None = Query(default=None, gt=0),
    materia_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("ASIGNACIONES")),
):
    q = db.query(AsignacionDocente)
    if gestion_id is not None:
        q = q.filter(AsignacionDocente.gestion_id == gestion_id)
    elif gestion is not None:
        q = q.join(Gestion, Gestion.id == AsignacionDocente.gestion_id).filter(
            Gestion.nombre == gestion
        )
    if docente_id is not None:
        q = q.filter(AsignacionDocente.docente_id == docente_id)
    if curso_id is not None:
        q = q.filter(AsignacionDocente.curso_id == curso_id)
    if paralelo_id is not None:
        q = q.filter(AsignacionDocente.paralelo_id == paralelo_id)
    if materia_id is not None:
        q = q.filter(AsignacionDocente.materia_id == materia_id)
    return q.order_by(AsignacionDocente.id.asc()).all()
