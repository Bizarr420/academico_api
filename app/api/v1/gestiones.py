from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.deps_extra import require_role_and_view, require_view
from app.db.models import Gestion, Usuario
from app.schemas.gestiones import GestionCreate, GestionOut, GestionUpdate

router = APIRouter(tags=["gestiones"])


@router.get("/", response_model=List[GestionOut])
def listar_gestiones(
    db: Session = Depends(get_db),
    solo_activas: bool = Query(False),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    _: Usuario = Depends(require_view("GESTIONES")),
):
    q = db.query(Gestion).order_by(Gestion.fecha_inicio.desc())
    if solo_activas:
        q = q.filter(Gestion.activo == 1)
    return q.offset(offset).limit(limit).all()


@router.get("/{gestion_id}", response_model=GestionOut)
def obtener_gestion(
    gestion_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("GESTIONES")),
):
    gestion = db.get(Gestion, gestion_id)
    if not gestion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gestión no encontrada")
    return gestion


@router.post(
    "/",
    response_model=GestionOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_gestion(
    payload: GestionCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_role_and_view({"admin"}, "GESTIONES")),
):
    if payload.fecha_fin < payload.fecha_inicio:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="fecha_fin debe ser mayor o igual a fecha_inicio")

    existente = db.query(Gestion).filter(Gestion.nombre == payload.nombre).first()
    if existente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Gestión ya existe")

    gestion = Gestion(**payload.model_dump())
    db.add(gestion)
    db.commit()
    db.refresh(gestion)
    return gestion


@router.patch(
    "/{gestion_id}",
    response_model=GestionOut,
)
def actualizar_gestion(
    gestion_id: int,
    payload: GestionUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_role_and_view({"admin"}, "GESTIONES")),
):
    gestion = db.get(Gestion, gestion_id)
    if not gestion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gestión no encontrada")

    data = payload.model_dump(exclude_unset=True)
    if "fecha_inicio" in data or "fecha_fin" in data:
        nueva_inicio = data.get("fecha_inicio", gestion.fecha_inicio)
        nueva_fin = data.get("fecha_fin", gestion.fecha_fin)
        if nueva_fin < nueva_inicio:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="fecha_fin debe ser mayor o igual a fecha_inicio")

    if "nombre" in data:
        duplicado = (
            db.query(Gestion)
            .filter(Gestion.nombre == data["nombre"], Gestion.id != gestion_id)
            .first()
        )
        if duplicado:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nombre ya en uso")

    for key, value in data.items():
        setattr(gestion, key, value)

    db.add(gestion)
    db.commit()
    db.refresh(gestion)
    return gestion
