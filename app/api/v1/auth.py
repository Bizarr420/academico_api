"""Authentication and session management endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session, selectinload
from pydantic import BaseModel, Field, ValidationError

from app.api.deps import AuthContext, get_db
from app.api.deps_extra import get_auth_context
from app.core.permissions import permission_cache
from app.core.security import create_access_token, hash_password, verify_password
from app.db.models import EstadoUsuarioEnum, Usuario
from app.schemas.usuarios import LoginResponse, SessionInfo, UsuarioOut


router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


async def _parse_login_payload(request: Request) -> LoginRequest:
    """Accept credentials as JSON or form data for backwards compatibility."""

    content_type = request.headers.get("content-type", "")
    if content_type.startswith("application/json"):
        try:
            payload = await request.json()
        except Exception as exc:  # pragma: no cover - body parsing guard
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrectos") from exc
    else:
        form = await request.form()
        payload = {"username": form.get("username"), "password": form.get("password")}

    try:
        return LoginRequest.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrectos") from exc


@router.post("/login", response_model=LoginResponse)
async def login(request: Request, db: Session = Depends(get_db)) -> LoginResponse:
    credentials = await _parse_login_payload(request)

    user = (
        db.query(Usuario)
        .options(selectinload(Usuario.persona), selectinload(Usuario.rol))
        .filter(Usuario.username == credentials.username)
        .first()
    )
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrectos")

    if user.estado != EstadoUsuarioEnum.ACTIVO:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario inactivo")

    if user.rol is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Rol no asignado")

    permissions = permission_cache.get_permissions(db, user.rol_id)
    token = create_access_token(
        {
            "user_id": user.id,
            "username": user.username,
            "rol_codigo": user.rol.codigo,
        }
    )

    return LoginResponse(
        access_token=token,
        user=UsuarioOut.model_validate(user, from_attributes=True),
        rol_codigo=user.rol.codigo,
        permisos=sorted(permissions),
    )


@router.get("/me", response_model=SessionInfo)
def me(context: AuthContext = Depends(get_auth_context)) -> SessionInfo:
    return SessionInfo(
        user=UsuarioOut.model_validate(context.user, from_attributes=True),
        rol_codigo=context.rol_codigo,
        permisos=sorted(context.permissions),
    )


@router.get("/me/permisos", response_model=list[str])
def mis_permisos(context: AuthContext = Depends(get_auth_context)) -> list[str]:
    return sorted(context.permissions)


class PasswordChangeIn(BaseModel):
    old_password: str = Field(min_length=6)
    new_password: str = Field(min_length=6)


@router.post("/change-password")
def change_password(
    payload: PasswordChangeIn,
    db: Session = Depends(get_db),
    context: AuthContext = Depends(get_auth_context),
) -> dict[str, Any]:
    usuario = context.user
    if not verify_password(payload.old_password, usuario.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrectos")

    usuario.password_hash = hash_password(payload.new_password)
    db.add(usuario)
    db.commit()
    return {"detail": "Contraseña actualizada"}
