from typing import List, Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.deps_extra import require_view
from app.db.models import Usuario, Vista
from app.schemas.roles import VistaOut

router = APIRouter(tags=["vistas"])


@router.get("/", response_model=List[VistaOut])
def listar_vistas(
    db: Session = Depends(get_db),
    estado: Literal["ACTIVO", "INACTIVO", "TODOS"] = Query("ACTIVO"),
    _: Usuario = Depends(require_view("VISTAS")),
):
    query = db.query(Vista).order_by(Vista.nombre)
    if estado != "TODOS":
        query = query.filter(Vista.estado == estado)
    return query.all()
