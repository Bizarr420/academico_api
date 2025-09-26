from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.deps_extra import require_role
from app.db.models import Rol
from app.schemas.roles import RolCreate, RolOut

router = APIRouter(tags=["roles"])


@router.get("/", response_model=List[RolOut])
def listar_roles(
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    return (
        db.query(Rol)
        .order_by(Rol.id)
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/{rol_id}", response_model=RolOut)
def obtener_rol(rol_id: int, db: Session = Depends(get_db)):
    rol = db.get(Rol, rol_id)
    if not rol:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")
    return rol


@router.post(
    "/",
    response_model=RolOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin"))],
)
def crear_rol(payload: RolCreate, db: Session = Depends(get_db)):
    existente = (
        db.query(Rol)
        .filter((Rol.nombre == payload.nombre) | (Rol.codigo == payload.codigo))
        .first()
    )
    if existente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rol ya existe")

    rol = Rol(nombre=payload.nombre, codigo=payload.codigo)
    db.add(rol)
    db.commit()
    db.refresh(rol)
    return rol


@router.put(
    "/{rol_id}",
    response_model=RolOut,
    dependencies=[Depends(require_role("admin"))],
)
def actualizar_rol(rol_id: int, payload: RolCreate, db: Session = Depends(get_db)):
    rol = db.get(Rol, rol_id)
    if not rol:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")

    duplicado = (
        db.query(Rol)
        .filter(
            ((Rol.nombre == payload.nombre) | (Rol.codigo == payload.codigo))
            & (Rol.id != rol_id)
        )
        .first()
    )
    if duplicado:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nombre o código ya en uso")

    rol.nombre = payload.nombre
    rol.codigo = payload.codigo
    db.add(rol)
    db.commit()
    db.refresh(rol)
    return rol
