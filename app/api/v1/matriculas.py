from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.deps import get_db
from app.api.deps_extra import require_view
from app.db.models import Matricula, AsignacionDocente, Estudiante, Usuario
from app.schemas.matriculas import MatriculaCreate, MatriculaRead

router = APIRouter(tags=["matriculas"])

@router.post("/", response_model=MatriculaRead)
def create_matricula(
    data: MatriculaCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("MATRICULAS")),
):
    # valida asignación / estudiante
    if not db.get(AsignacionDocente, data.asignacion_id):
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    if not db.get(Estudiante, data.estudiante_id):
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    # idempotente: si ya existe, regrésalo
    existing = db.execute(
        select(Matricula).where(
            Matricula.asignacion_id == data.asignacion_id,
            Matricula.estudiante_id == data.estudiante_id,
        )
    ).scalar_one_or_none()
    if existing:
        return existing

    m = Matricula(**data.model_dump())
    db.add(m)
    db.commit()
    db.refresh(m)
    return m

@router.get("/", response_model=list[MatriculaRead])
def list_matriculas(
    asignacion_id: int | None = None,
    estudiante_id: int | None = None,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("MATRICULAS")),
):
    stmt = select(Matricula)
    if asignacion_id is not None:
        stmt = stmt.where(Matricula.asignacion_id == asignacion_id)
    if estudiante_id is not None:
        stmt = stmt.where(Matricula.estudiante_id == estudiante_id)
    return db.execute(stmt).scalars().all()
