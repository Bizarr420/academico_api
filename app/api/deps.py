"""Common FastAPI dependencies used across the API layer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet, Iterable

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session, selectinload

from app.core.permissions import permission_cache
from app.core.security import decode_token
from app.db.models import EstadoUsuarioEnum, Usuario
from app.db.session import SessionLocal


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@dataclass(slots=True)
class AuthContext:
    """Represents an authenticated request along with its permissions."""

    user: Usuario
    rol_codigo: str
    permissions: FrozenSet[str]


def get_db() -> Iterable[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_auth(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> AuthContext:
    payload = decode_token(token)
    try:
        user_id = int(payload.get("user_id"))
    except (TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

    user = (
        db.query(Usuario)
        .options(selectinload(Usuario.rol))
        .filter(Usuario.id == user_id)
        .first()
    )
    if not user or user.estado != EstadoUsuarioEnum.ACTIVO:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")

    username = payload.get("username")
    if not username or user.username != username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")

    if user.rol is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Rol no asignado")

    permissions = permission_cache.get_permissions(db, user.rol_id)
    context = AuthContext(
        user=user,
        rol_codigo=user.rol.codigo,
        permissions=permissions,
    )

    request.state.user_id = user.id
    request.state.rol_codigo = context.rol_codigo
    request.state.permisos = sorted(permissions)

    return context


def get_current_user(context: AuthContext = Depends(require_auth)) -> Usuario:
    return context.user


def require_roles(*roles_validos: str):
    allowed = {rol.upper() for rol in roles_validos if rol}

    def dependency(context: AuthContext = Depends(require_auth)) -> Usuario:
        if allowed and context.rol_codigo.upper() not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permisos insuficientes",
            )
        return context.user

    return dependency


def require_role(*roles: str):
    return require_roles(*roles)
