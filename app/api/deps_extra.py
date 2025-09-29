"""Additional reusable dependencies for role-based access control."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user, get_db
from app.db.models import Rol, Usuario


def _load_rol(user: Usuario, db: Session) -> Rol | None:
    if not getattr(user, "rol_id", None):
        return None
    return (
        db.query(Rol)
        .options(selectinload(Rol.vistas))
        .filter(Rol.id == user.rol_id)
        .first()
    )


def _normalise(values: Sequence[str] | Iterable[str]) -> set[str]:
    return {str(value).upper() for value in values}


def require_view(code: str):
    required = str(code).upper()

    def dependency(
        user: Usuario = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> Usuario:
        rol = _load_rol(user, db)
        if rol and any(v.codigo.upper() == required for v in rol.vistas):
            return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permisos insuficientes",
        )

    return dependency


def require_role(*codes: Iterable[str] | str):
    if len(codes) == 1 and not isinstance(codes[0], str):
        allowed = _normalise(codes[0])
    else:
        allowed = _normalise(codes)

    def dependency(
        user: Usuario = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> Usuario:
        rol = _load_rol(user, db)
        nombre = rol.nombre.upper() if rol and rol.nombre else None
        if nombre in allowed:
            return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permisos insuficientes",
        )

    return dependency


def require_role_and_view(roles: Iterable[str], view_code: str):
    allowed_roles = _normalise(roles)
    required_view = str(view_code).upper()

    def dependency(
        user: Usuario = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> Usuario:
        rol = _load_rol(user, db)
        nombre = rol.nombre.upper() if rol and rol.nombre else None
        if nombre not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permisos insuficientes",
            )
        if not any(v.codigo.upper() == required_view for v in rol.vistas):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permisos insuficientes",
            )
        return user

    return dependency
