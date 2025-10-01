"""User management endpoints with permission checks."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.api.deps import AuthContext, get_db
from app.api.deps_extra import get_auth_context, require_permission
from app.core.audit import registrar_auditoria
from app.core.permissions import permission_cache
from app.core.security import hash_password
from app.db.models import EstadoUsuarioEnum, Persona, Rol, Usuario
from app.schemas.usuarios import (
    SessionInfo,
    UsuarioCreate,
    UsuarioOut,
    UsuarioPasswordUpdate,
    UsuarioRoleUpdate,
    UsuarioUpdate,
)


router = APIRouter(tags=["usuarios"])


@router.get("/", response_model=List[UsuarioOut])
def listar_usuarios(
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    rol_id: int | None = Query(None, ge=1),
    estado: EstadoUsuarioEnum | None = Query(None),
    _: Usuario = Depends(require_permission("USUARIOS")),
) -> List[UsuarioOut]:
    query = (
        db.query(Usuario)
        .options(selectinload(Usuario.persona), selectinload(Usuario.rol))
        .order_by(Usuario.id)
    )
    if rol_id is not None:
        query = query.filter(Usuario.rol_id == rol_id)
    if estado is not None:
        query = query.filter(Usuario.estado == estado)
    usuarios = query.offset(offset).limit(limit).all()
    return usuarios


@router.get("/{usuario_id}", response_model=UsuarioOut)
def obtener_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permission("USUARIOS")),
) -> UsuarioOut:
    usuario = (
        db.query(Usuario)
        .options(selectinload(Usuario.persona), selectinload(Usuario.rol))
        .filter(Usuario.id == usuario_id)
        .first()
    )
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return usuario


@router.post("/", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def crear_usuario(
    payload: UsuarioCreate,
    request: Request,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permission("USUARIOS")),
    context: AuthContext = Depends(get_auth_context),
) -> UsuarioOut:
    if (
        db.query(Usuario)
        .filter(Usuario.username == payload.username)
        .first()
    ):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Usuario ya existe")

    persona = db.get(Persona, payload.persona_id)
    if not persona:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Persona no encontrada")

    rol = db.get(Rol, payload.rol_id)
    if not rol:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")

    usuario = Usuario(
        persona_id=payload.persona_id,
        username=payload.username,
        password_hash=hash_password(payload.password),
        rol_id=payload.rol_id,
        estado=EstadoUsuarioEnum.ACTIVO,
    )

    db.add(usuario)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Usuario ya existe") from exc
    db.refresh(usuario)

    registrar_auditoria(
        db,
        actor_id=context.user.id,
        accion="CREAR",
        entidad="USUARIO",
        entidad_id=usuario.id,
        request=request,
    )

    usuario = (
        db.query(Usuario)
        .options(selectinload(Usuario.persona), selectinload(Usuario.rol))
        .filter(Usuario.id == usuario.id)
        .first()
    )
    return UsuarioOut.model_validate(usuario, from_attributes=True)


@router.patch("/{usuario_id}", response_model=UsuarioOut)
def actualizar_usuario(
    usuario_id: int,
    payload: UsuarioUpdate,
    request: Request,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permission("USUARIOS")),
    context: AuthContext = Depends(get_auth_context),
) -> UsuarioOut:
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    if payload.rol_id is not None:
        rol = db.get(Rol, payload.rol_id)
        if not rol:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(usuario, key, value)

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    registrar_auditoria(
        db,
        actor_id=context.user.id,
        accion="ACTUALIZAR",
        entidad="USUARIO",
        entidad_id=usuario.id,
        request=request,
    )

    usuario = (
        db.query(Usuario)
        .options(selectinload(Usuario.persona), selectinload(Usuario.rol))
        .filter(Usuario.id == usuario.id)
        .first()
    )
    return UsuarioOut.model_validate(usuario, from_attributes=True)


@router.put("/{usuario_id}/rol", response_model=UsuarioOut)
def actualizar_rol_usuario(
    usuario_id: int,
    payload: UsuarioRoleUpdate,
    request: Request,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permission("USUARIOS")),
    context: AuthContext = Depends(get_auth_context),
) -> UsuarioOut:
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    rol = db.get(Rol, payload.rol_id)
    if not rol:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")

    usuario.rol_id = payload.rol_id
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    registrar_auditoria(
        db,
        actor_id=context.user.id,
        accion="CAMBIAR_ROL",
        entidad="USUARIO",
        entidad_id=usuario.id,
        request=request,
    )

    usuario = (
        db.query(Usuario)
        .options(selectinload(Usuario.persona), selectinload(Usuario.rol))
        .filter(Usuario.id == usuario.id)
        .first()
    )
    return UsuarioOut.model_validate(usuario, from_attributes=True)


@router.put("/{usuario_id}/password", response_model=SessionInfo)
def actualizar_password_usuario(
    usuario_id: int,
    payload: UsuarioPasswordUpdate,
    request: Request,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permission("USUARIOS")),
    context: AuthContext = Depends(get_auth_context),
) -> SessionInfo:
    usuario = (
        db.query(Usuario)
        .options(selectinload(Usuario.persona), selectinload(Usuario.rol))
        .filter(Usuario.id == usuario_id)
        .first()
    )
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    usuario.password_hash = hash_password(payload.password)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    registrar_auditoria(
        db,
        actor_id=context.user.id,
        accion="CAMBIAR_PASSWORD",
        entidad="USUARIO",
        entidad_id=usuario.id,
        request=request,
    )

    permisos = sorted(permission_cache.get_permissions(db, usuario.rol_id))

    return SessionInfo(
        user=UsuarioOut.model_validate(usuario, from_attributes=True),
        rol_codigo=usuario.rol.codigo,
        permisos=permisos,
    )
