from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_db, get_current_user
from app.api.deps_extra import require_role
from app.core.security import hash_password
from app.db.models import EstadoUsuarioEnum, Persona, Usuario
from app.schemas.usuarios import UsuarioCreate, UsuarioOut, UsuarioUpdate

router = APIRouter(tags=["usuarios"])


@router.get("/", response_model=List[UsuarioOut], dependencies=[Depends(get_current_user)])
def listar_usuarios(
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    rol_id: int | None = Query(None, ge=1),
    estado: EstadoUsuarioEnum | None = Query(None),
):
    q = db.query(Usuario).options(selectinload(Usuario.persona))
    if rol_id is not None:
        q = q.filter(Usuario.rol_id == rol_id)
    if estado is not None:
        q = q.filter(Usuario.estado == estado)
    usuarios = q.order_by(Usuario.id).offset(offset).limit(limit).all()
    return usuarios


@router.get("/{usuario_id}", response_model=UsuarioOut, dependencies=[Depends(get_current_user)])
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = (
        db.query(Usuario)
        .options(selectinload(Usuario.persona))
        .filter(Usuario.id == usuario_id)
        .first()
    )
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return usuario


@router.post(
    "/",
    response_model=UsuarioOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin"))],
)
def crear_usuario(payload: UsuarioCreate, db: Session = Depends(get_db)):
    if db.query(Usuario).filter(Usuario.username == payload.username).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario ya existe")

    persona = db.get(Persona, payload.persona_id)
    if not persona:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Persona no encontrada")

    usuario = Usuario(
        persona_id=payload.persona_id,
        username=payload.username,
        password_hash=hash_password(payload.password),
        rol_id=payload.rol_id,
        estado=EstadoUsuarioEnum.ACTIVO,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return UsuarioOut.model_validate(usuario, from_attributes=True)


@router.patch(
    "/{usuario_id}",
    response_model=UsuarioOut,
    dependencies=[Depends(require_role("admin"))],
)
def actualizar_usuario(usuario_id: int, payload: UsuarioUpdate, db: Session = Depends(get_db)):
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(usuario, key, value)

    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return UsuarioOut.model_validate(usuario, from_attributes=True)
