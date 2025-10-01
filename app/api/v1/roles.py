"""Role management endpoints with RBAC enforcement."""

from __future__ import annotations

import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.api.deps import AuthContext, get_db
from app.api.deps_extra import get_auth_context, require_permission
from app.core.audit import registrar_auditoria
from app.core.permissions import permission_cache
from app.db.models import Rol
from app.schemas.roles import RolCreate, RolOut, RolUpdate


router = APIRouter(tags=["roles"])


@router.get("/", response_model=List[RolOut])
def listar_roles(
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    _: AuthContext = Depends(require_permission("ROLES")),
) -> List[RolOut]:
    roles = (
        db.query(Rol)
        .options(selectinload(Rol.vistas))
        .order_by(Rol.id)
        .offset(offset)
        .limit(limit)
        .all()
    )
    return roles


@router.get("/{rol_id}", response_model=RolOut)
def obtener_rol(
    rol_id: int,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(require_permission("ROLES")),
) -> RolOut:
    rol = (
        db.query(Rol)
        .options(selectinload(Rol.vistas))
        .filter(Rol.id == rol_id)
        .first()
    )
    if not rol:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")
    return rol


@router.get("/{rol_id}/vistas", response_model=RolOut)
def obtener_rol_con_vistas(
    rol_id: int,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(require_permission("ROLES")),
) -> RolOut:
    return obtener_rol(rol_id, db)


@router.post("/", response_model=RolOut, status_code=status.HTTP_201_CREATED)
def crear_rol(
    payload: RolCreate,
    request: Request,
    db: Session = Depends(get_db),
    context: AuthContext = Depends(get_auth_context),
) -> RolOut:
    try:
        result = db.execute(
            text("CALL sp_role_create(:nombre, :codigo, :vista_ids)"),
            {
                "nombre": payload.nombre,
                "codigo": payload.codigo,
                "vista_ids": json.dumps(payload.vista_ids or []),
            },
        )
        created = result.mappings().first()
        result.close()
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Rol ya existe") from exc

    if not created:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No fue posible crear el rol")

    role_id = created.get("id") or created.get("rol_id")
    if role_id is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No fue posible determinar el rol creado")

    permission_cache.invalidate_role(role_id)
    registrar_auditoria(
        db,
        actor_id=context.user.id,
        accion="CREAR",
        entidad="ROL",
        entidad_id=role_id,
        request=request,
    )

    rol = (
        db.query(Rol)
        .options(selectinload(Rol.vistas))
        .filter(Rol.id == role_id)
        .first()
    )
    if not rol:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Rol creado pero no encontrado")
    return rol


@router.put("/{rol_id}", response_model=RolOut)
def actualizar_rol(
    rol_id: int,
    payload: RolUpdate,
    request: Request,
    db: Session = Depends(get_db),
    context: AuthContext = Depends(get_auth_context),
) -> RolOut:
    rol = (
        db.query(Rol)
        .options(selectinload(Rol.vistas))
        .filter(Rol.id == rol_id)
        .first()
    )
    if not rol:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")

    if payload.nombre is not None:
        rol.nombre = payload.nombre
    if payload.codigo is not None:
        rol.codigo = payload.codigo

    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Código de rol duplicado") from exc

    if payload.vista_ids is not None:
        try:
            result = db.execute(
                text("CALL sp_role_replace_vistas(:role_id, :vista_ids)"),
                {
                    "role_id": rol_id,
                    "vista_ids": json.dumps(payload.vista_ids),
                },
            )
            result.close()
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Vista duplicada") from exc

    db.commit()

    permission_cache.invalidate_role(rol_id)
    registrar_auditoria(
        db,
        actor_id=context.user.id,
        accion="ACTUALIZAR",
        entidad="ROL",
        entidad_id=rol_id,
        request=request,
    )

    db.refresh(rol)
    rol = (
        db.query(Rol)
        .options(selectinload(Rol.vistas))
        .filter(Rol.id == rol_id)
        .first()
    )
    return rol
