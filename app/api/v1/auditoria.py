from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.deps_extra import require_role_and_view
from app.db.models import AuditLog, Usuario
from app.schemas.audit import AuditLogPage

router = APIRouter(tags=["auditoria"])


@router.get("/", response_model=AuditLogPage)
def listar_auditoria(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    actor_id: int | None = Query(None, ge=1),
    accion: str | None = Query(None, min_length=1, max_length=60),
    entidad: str | None = Query(None, min_length=1, max_length=60),
    _: Usuario = Depends(require_role_and_view({"admin"}, "AUDITORIA")),
) -> AuditLogPage:
    q = db.query(AuditLog)
    if actor_id is not None:
        q = q.filter(AuditLog.actor_id == actor_id)
    if accion is not None:
        q = q.filter(AuditLog.accion.ilike(f"%{accion}%"))
    if entidad is not None:
        q = q.filter(AuditLog.entidad.ilike(f"%{entidad}%"))

    total = q.count()
    rows = (
        q.order_by(AuditLog.creado_en.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    return AuditLogPage(total=total, page=page, size=size, items=rows)
