"""Common FastAPI dependencies used across the API layer."""

from __future__ import annotations

from typing import Iterable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.models import EstadoUsuarioEnum, Usuario
from app.db.session import SessionLocal


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_db() -> Iterable[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )

    try:
        payload = decode_token(token)
    except Exception as exc:  # pragma: no cover - defensive
        raise credentials_error from exc

    username = payload.get("sub")
    if not username:
        raise credentials_error

    user = db.query(Usuario).filter(Usuario.username == username).first()
    if not user or user.estado != EstadoUsuarioEnum.ACTIVO:
        raise credentials_error

    return user


def require_roles(*roles_validos: str):
    """Temporarily bypass role enforcement while roles are disabled."""

    def dependency(current_user: Usuario = Depends(get_current_user)) -> Usuario:
        return current_user

    return dependency


def require_role(*roles: str):
    """Alias retained for backwards compatibility."""

    return require_roles(*roles)
