"""Utility helpers for permission caching and retrieval."""

from __future__ import annotations

from threading import RLock
from typing import FrozenSet, Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Vista, rol_vistas


class RolePermissionCache:
    """In-memory cache that stores permissions per role identifier."""

    def __init__(self) -> None:
        self._store: dict[int, FrozenSet[str]] = {}
        self._lock = RLock()

    def get_permissions(self, db: Session, role_id: int) -> FrozenSet[str]:
        """Return the set of permission codes granted to ``role_id``."""

        with self._lock:
            cached = self._store.get(role_id)
        if cached is not None:
            return cached

        result = (
            db.execute(
                select(Vista.codigo)
                .join(rol_vistas, Vista.id == rol_vistas.c.vista_id)
                .where(rol_vistas.c.rol_id == role_id)
            )
            .scalars()
            .all()
        )
        permissions = frozenset(result)
        with self._lock:
            self._store[role_id] = permissions
        return permissions

    def invalidate_role(self, role_id: int) -> None:
        """Remove cached permissions for ``role_id`` if present."""

        with self._lock:
            self._store.pop(role_id, None)

    def invalidate_many(self, role_ids: Iterable[int]) -> None:
        """Remove cached permissions for several roles."""

        with self._lock:
            for role_id in role_ids:
                self._store.pop(role_id, None)

    def clear(self) -> None:
        """Remove all cached permission entries."""

        with self._lock:
            self._store.clear()


permission_cache = RolePermissionCache()

