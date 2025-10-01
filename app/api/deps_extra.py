"""Additional reusable dependencies for role-based access control."""

from __future__ import annotations

from collections.abc import Iterable

from fastapi import Depends

from app.api.deps import get_current_user
from app.db.models import Usuario


def require_view(_code: str):
    """Temporarily bypass view enforcement while roles are disabled."""

    def dependency(user: Usuario = Depends(get_current_user)) -> Usuario:
        return user

    return dependency


def require_role(*_codes: Iterable[str] | str):
    """Temporarily bypass role enforcement while roles are disabled."""

    def dependency(user: Usuario = Depends(get_current_user)) -> Usuario:
        return user

    return dependency


def require_role_and_view(_roles: Iterable[str], _view_code: str):
    """Temporarily bypass combined role/view enforcement while roles are disabled."""

    def dependency(user: Usuario = Depends(get_current_user)) -> Usuario:
        return user

    return dependency
