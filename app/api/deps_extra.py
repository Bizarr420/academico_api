"""Additional reusable dependencies for role-based access control."""

from __future__ import annotations

from collections.abc import Iterable

from fastapi import Depends, HTTPException, status

from app.api.deps import AuthContext, require_auth
from app.db.models import Usuario


def get_auth_context(context: AuthContext = Depends(require_auth)) -> AuthContext:
    """Expose the authenticated context to API endpoints."""

    return context


def require_permission(view_code: str):
    required = view_code.upper()

    def dependency(context: AuthContext = Depends(require_auth)) -> Usuario:
        if required not in context.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permiso denegado",
            )
        return context.user

    return dependency


def require_view(code: str):
    """Compatibility helper that enforces access to ``code``."""

    return require_permission(code)


def require_role(*codes: Iterable[str] | str):
    allowed = {
        value.upper()
        for item in codes
        for value in (item if isinstance(item, Iterable) and not isinstance(item, str) else [item])
        if value
    }

    def dependency(context: AuthContext = Depends(require_auth)) -> Usuario:
        if allowed and context.rol_codigo.upper() not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permiso denegado",
            )
        return context.user

    return dependency


def require_role_and_view(roles: Iterable[str], view_code: str):
    allowed_roles = {role.upper() for role in roles}
    permission = view_code.upper()

    def dependency(context: AuthContext = Depends(require_auth)) -> Usuario:
        if allowed_roles and context.rol_codigo.upper() not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permiso denegado",
            )
        if permission not in context.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permiso denegado",
            )
        return context.user

    return dependency
