"""Utilities for persisting audit logs."""

from __future__ import annotations

from typing import Any

from fastapi import Request
from sqlalchemy.orm import Session

from app.db.models import AuditLog


def registrar_auditoria(
    db: Session,
    *,
    actor_id: int | None,
    accion: str,
    entidad: str,
    entidad_id: Any | None,
    request: Request | None = None,
) -> AuditLog:
    """Persist an :class:`AuditLog` entry immediately.

    Parameters
    ----------
    db:
        Active SQLAlchemy session.
    actor_id:
        Identifier of the user performing the action (``None`` for anonymous).
    accion:
        Short verb describing the action (``CREAR``, ``ACTUALIZAR`` ...).
    entidad:
        Name of the affected entity (``USUARIO``, ``ROL`` ...).
    entidad_id:
        Identifier of the affected entity. Stored as a string to accommodate
        composite identifiers.
    request:
        Optional request object used to extract IP and user agent metadata.
    """

    ip_origen = None
    user_agent = None
    if request is not None:
        client = request.client
        if client:
            ip_origen = client.host
        user_agent = request.headers.get("user-agent")

    log = AuditLog(
        actor_id=actor_id,
        accion=accion,
        entidad=entidad,
        entidad_id=str(entidad_id) if entidad_id is not None else None,
        ip_origen=ip_origen,
        user_agent=user_agent,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
