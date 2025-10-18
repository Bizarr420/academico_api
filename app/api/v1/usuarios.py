from __future__ import annotations
def error_response(code: str, message: str, details: str | None = None, status_code: int = 400):
    return HTTPException(
        status_code=status_code,
        detail={
            "code": code,
            "message": message,
            "details": details,
        },
    )
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

# --- Endpoints para activar/desactivar usuario ---
@router.patch("/{usuario_id}/desactivar", response_model=UsuarioOut)
def desactivar_usuario(
    usuario_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permission("USUARIOS")),
    context: AuthContext = Depends(get_auth_context),
) -> UsuarioOut:
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise error_response(
            code="USER_NOT_FOUND",
            message="Usuario no encontrado",
            details=f"ID: {usuario_id}",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    # No permitir desactivar el propio usuario
    if usuario.id == context.user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes desactivar tu propio usuario"
        )
    
    usuario.estado = EstadoUsuarioEnum.INACTIVO
    from datetime import datetime
    usuario.eliminado_en = datetime.utcnow()
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    registrar_auditoria(
        db,
        actor_id=context.user.id,
        accion="DESACTIVAR",
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

@router.patch("/{usuario_id}/activar", response_model=UsuarioOut)
def activar_usuario(
    usuario_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permission("USUARIOS")),
    context: AuthContext = Depends(get_auth_context),
) -> UsuarioOut:
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    
    usuario.estado = EstadoUsuarioEnum.ACTIVO
    usuario.eliminado_en = None
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    
    registrar_auditoria(
        db,
        actor_id=context.user.id,
        accion="ACTIVAR",
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


# --- Endpoint compatible sin id en la ruta: /api/usuarios/desactivar ---
from pydantic import BaseModel


class UsuarioIdPayload(BaseModel):
    usuario_id: int



@router.patch("/desactivar", response_model=UsuarioOut)
def desactivar_usuario_por_payload(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permission("USUARIOS")),
    context: AuthContext = Depends(get_auth_context),
) -> UsuarioOut:
    """Compatibilidad para clientes que llaman a /api/usuarios/desactivar con JSON {usuario_id}.
    Retorna 400 si falta usuario_id o no es un entero.
    """
    usuario_id = payload.get("usuario_id")
    if not isinstance(usuario_id, int):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Se requiere usuario_id entero en el body")

    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    # No permitir desactivar el propio usuario
    if usuario.id == context.user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes desactivar tu propio usuario"
        )

    usuario.estado = EstadoUsuarioEnum.INACTIVO
    from datetime import datetime
    usuario.eliminado_en = datetime.utcnow()
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    registrar_auditoria(
        db,
        actor_id=context.user.id,
        accion="DESACTIVAR",
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


@router.get("/", response_model=List[UsuarioOut])
def listar_usuarios(
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    rol_id: int | None = Query(None, ge=1),
    estado: EstadoUsuarioEnum | None = Query(None),
    search: str | None = Query(None),
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
    if search:
        search = search.strip()
        if search:
            like_pattern = f"%{search}%"
            query = query.join(Persona).filter(
                (Usuario.username.ilike(like_pattern)) |
                (Persona.nombres.ilike(like_pattern)) |
                (Persona.apellidos.ilike(like_pattern))
            )

    total = query.count()
    usuarios = query.offset(offset).limit(limit).all()
    
    # Incluir el total en los headers de la respuesta
    from fastapi import Response
    response = Response()
    response.headers["X-Total-Count"] = str(total)
    
    # Como necesitamos retornar tanto la respuesta como los headers,
    # usamos el modelo directamente para los usuarios
    return [UsuarioOut.model_validate(u, from_attributes=True) for u in usuarios]


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

    # Create persona if persona data is provided
    persona_id = None
    if payload.persona:
        persona_obj = Persona(
            nombres=payload.persona.nombres,
            apellidos=payload.persona.apellidos,
            sexo=payload.persona.sexo,
            fecha_nacimiento=payload.persona.fecha_nacimiento,
            celular=payload.persona.celular,
            direccion=payload.persona.direccion,
        )
        db.add(persona_obj)
        db.flush()  # get persona_obj.id
        persona_id = persona_obj.id
        # Optionally create CI record if provided
        if payload.persona.ci_numero:
            from app.db.models import CIPersona
            ci_obj = CIPersona(
                persona_id=persona_id,
                ci_numero=payload.persona.ci_numero,
                ci_complemento=payload.persona.ci_complemento,
                ci_expedicion=payload.persona.ci_expedicion,
            )
            db.add(ci_obj)
    elif payload.persona_id:
        persona = db.get(Persona, payload.persona_id)
        if not persona:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Persona no encontrada")
        persona_id = payload.persona_id
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Se requiere persona o persona_id")

    rol = db.get(Rol, payload.rol_id)
    if not rol:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")

    usuario = Usuario(
        persona_id=persona_id,
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

    # Validar username único si se está actualizando
    if payload.username is not None and payload.username != usuario.username:
        existing_user = (
            db.query(Usuario)
            .filter(Usuario.username == payload.username, Usuario.id != usuario_id)
            .first()
        )
        if existing_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username ya existe")

    if payload.rol_id is not None:
        rol = db.get(Rol, payload.rol_id)
        if not rol:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")

    # Validar estado
    if payload.estado is not None and payload.estado not in EstadoUsuarioEnum:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Estado inválido")


    data = payload.model_dump(exclude_unset=True)
    # Actualizar datos de usuario
    for key, value in data.items():
        if key != "persona":
            setattr(usuario, key, value)

    # Actualizar datos de persona vinculada si se envía
    if "persona" in data and usuario.persona and data["persona"]:
        persona_data = data["persona"]
        for pkey, pvalue in persona_data.items():
            if pvalue is not None:
                setattr(usuario.persona, pkey, pvalue)
        db.add(usuario.persona)

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
