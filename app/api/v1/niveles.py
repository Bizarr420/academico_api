from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.deps_extra import require_role_and_view, require_view
from app.db.models import Nivel, Usuario
from app.schemas.niveles import NivelCreate, NivelOut, NivelUpdate

router = APIRouter(tags=["niveles"])


@router.get("/", response_model=List[NivelOut])
def listar_niveles(
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    _: Usuario = Depends(require_view("NIVELES")),
):
    return (
        db.query(Nivel)
        .order_by(Nivel.id)
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/{nivel_id}", response_model=NivelOut)
def obtener_nivel(
    nivel_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("NIVELES")),
):
    nivel = db.get(Nivel, nivel_id)
    if not nivel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nivel no encontrado")
    return nivel


@router.post(
    "/",
    response_model=NivelOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_nivel(
    payload: NivelCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_role_and_view({"admin"}, "NIVELES")),
):
    existente = db.query(Nivel).filter(Nivel.nombre == payload.nombre).first()
    if existente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nivel ya existe")

    nivel = Nivel(**payload.model_dump())
    db.add(nivel)
    db.commit()
    db.refresh(nivel)
    return nivel


@router.patch(
    "/{nivel_id}",
    response_model=NivelOut,
)
def actualizar_nivel(
    nivel_id: int,
    payload: NivelUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_role_and_view({"admin"}, "NIVELES")),
):
    nivel = db.get(Nivel, nivel_id)
    if not nivel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nivel no encontrado")

    data = payload.model_dump(exclude_unset=True)
    if "nombre" in data:
        duplicado = (
            db.query(Nivel)
            .filter(Nivel.nombre == data["nombre"], Nivel.id != nivel_id)
            .first()
        )
        if duplicado:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nombre ya en uso")

    for key, value in data.items():
        setattr(nivel, key, value)

    db.add(nivel)
    db.commit()
    db.refresh(nivel)
    return nivel
