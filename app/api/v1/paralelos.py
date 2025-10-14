from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.deps_extra import require_view
from app.db.models import Paralelo, Usuario

router = APIRouter()

@router.get("/")
def listar_paralelos(
    db: Session = Depends(get_db),
    estado: Literal["ACTIVO", "INACTIVO", "TODOS"] = Query("ACTIVO"),
    _: Usuario = Depends(require_view("PARALELOS")),
):
    query = db.query(Paralelo).order_by(Paralelo.id.asc())
    if estado != "TODOS":
        query = query.filter(Paralelo.estado == estado)
    return query.all()

@router.post("/")
def crear_paralelo(
    data: dict,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("PARALELOS")),
):
    estado = data.get("estado")
    if estado is not None:
        estado_norm = str(estado).strip().upper()
        if estado_norm not in {"ACTIVO", "INACTIVO"}:
            raise HTTPException(status_code=400, detail="estado inválido")
        data["estado"] = estado_norm
    p = Paralelo(**data)
    db.add(p); db.commit(); db.refresh(p)
    return p
