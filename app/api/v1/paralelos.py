from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.deps_extra import require_view
from app.db.models import Paralelo, Usuario
from app.schemas.paralelos import ParaleloCreate


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
    data: ParaleloCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("PARALELOS")),
):
    p = Paralelo(**data.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p
