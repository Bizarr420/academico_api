"""Additional reusable dependencies for role-based access control."""

from __future__ import annotations

from collections.abc import Iterable

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db.models import Rol, Usuario


def require_role(*codes: Iterable[str] | str):
    if len(codes) == 1 and not isinstance(codes[0], str):
        allowed = {str(code).upper() for code in codes[0]}
    else:
        allowed = {str(code).upper() for code in codes}

    def dependency(
        user: Usuario = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> Usuario:
        rol_id = getattr(user, "rol_id", None)
        rol = db.get(Rol, rol_id) if rol_id else None
        nombre = rol.nombre.upper() if rol and rol.nombre else None
        if nombre in allowed:
            return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permisos insuficientes",
        )

    return dependency
