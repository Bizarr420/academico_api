from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.deps_extra import require_role
from app.db.models import Docente, Persona
from app.schemas.docentes import DocenteCreate, DocenteOut, DocenteUpdate

router = APIRouter(tags=["docentes"])


@router.get("/", response_model=List[DocenteOut])
def listar_docentes(
    db: Session = Depends(get_db),
    persona_id: int | None = Query(None, ge=1),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    q = db.query(Docente)
    if persona_id is not None:
        q = q.filter(Docente.persona_id == persona_id)
    return q.order_by(Docente.id).offset(offset).limit(limit).all()


@router.get("/{docente_id}", response_model=DocenteOut)
def obtener_docente(docente_id: int, db: Session = Depends(get_db)):
    docente = db.get(Docente, docente_id)
    if not docente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Docente no encontrado")
    return docente


@router.post(
    "/",
    response_model=DocenteOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin"))],
)
def crear_docente(payload: DocenteCreate, db: Session = Depends(get_db)):
    persona = db.get(Persona, payload.persona_id)
    if not persona:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Persona no encontrada")

    existe = db.query(Docente).filter(Docente.persona_id == payload.persona_id).first()
    if existe:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Docente ya existe para la persona")

    docente = Docente(**payload.model_dump())
    db.add(docente)
    db.commit()
    db.refresh(docente)
    return docente


@router.patch(
    "/{docente_id}",
    response_model=DocenteOut,
    dependencies=[Depends(require_role("admin"))],
)
def actualizar_docente(docente_id: int, payload: DocenteUpdate, db: Session = Depends(get_db)):
    docente = db.get(Docente, docente_id)
    if not docente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Docente no encontrado")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(docente, key, value)

    db.add(docente)
    db.commit()
    db.refresh(docente)
    return docente
