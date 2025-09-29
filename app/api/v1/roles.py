from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_db
from app.api.deps_extra import require_role_and_view, require_view
from app.core.audit import registrar_auditoria
from app.db.models import Rol, Usuario, Vista
from app.schemas.roles import RolCreate, RolOut, RolUpdate

router = APIRouter(tags=["roles"])


@router.get("/", response_model=List[RolOut])
def listar_roles(
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    _: Usuario = Depends(require_view("ROLES")),
):
    return (
        db.query(Rol)
        .options(selectinload(Rol.vistas))
        .order_by(Rol.id)
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/{rol_id}", response_model=RolOut)
def obtener_rol(
    rol_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("ROLES")),
):
    rol = db.query(Rol).options(selectinload(Rol.vistas)).filter(Rol.id == rol_id).first()
    if not rol:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")
    return rol


@router.post(
    "/",
    response_model=RolOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_rol(
    payload: RolCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role_and_view({"admin"}, "ROLES")),
):
    existente = (
        db.query(Rol)
        .filter((Rol.nombre == payload.nombre) | (Rol.codigo == payload.codigo))
        .first()
    )
    if existente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rol ya existe")

    vistas: list[Vista] = []
    if payload.vista_ids:
        ids = set(payload.vista_ids)
        vistas = db.query(Vista).filter(Vista.id.in_(ids)).all()
        if len(vistas) != len(ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Alguna vista especificada no existe",
            )

    rol = Rol(nombre=payload.nombre, codigo=payload.codigo, vistas=vistas)
    db.add(rol)
    db.commit()
    db.refresh(rol)
    registrar_auditoria(
        db,
        actor_id=current_user.id,
        accion="CREAR",
        entidad="ROL",
        entidad_id=rol.id,
        request=request,
    )
    return (
        db.query(Rol)
        .options(selectinload(Rol.vistas))
        .filter(Rol.id == rol.id)
        .first()
    )


@router.put(
    "/{rol_id}",
    response_model=RolOut,
)
def actualizar_rol(
    rol_id: int,
    payload: RolUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role_and_view({"admin"}, "ROLES")),
):
    rol = db.query(Rol).options(selectinload(Rol.vistas)).filter(Rol.id == rol_id).first()
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
    if payload.vista_ids is not None:
        ids = set(payload.vista_ids)
        vistas = db.query(Vista).filter(Vista.id.in_(ids)).all() if ids else []
        if len(vistas) != len(ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Alguna vista especificada no existe",
            )
        rol.vistas = vistas
    db.add(rol)
    db.commit()
    db.refresh(rol)
    registrar_auditoria(
        db,
        actor_id=current_user.id,
        accion="ACTUALIZAR",
        entidad="ROL",
        entidad_id=rol.id,
        request=request,
    )
    return (
        db.query(Rol)
        .options(selectinload(Rol.vistas))
        .filter(Rol.id == rol_id)
        .first()
    )
