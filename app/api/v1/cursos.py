# app/api/v1/cursos.py
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.deps_extra import require_role_and_view, require_view
from app.db.models import Curso, Paralelo, Usuario

router = APIRouter(tags=["cursos"])

@router.get("/")
def listar(
    offset: int = 0,
    limit: int = 50,
    estado: Literal["ACTIVO", "INACTIVO", "TODOS"] = Query("ACTIVO"),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("CURSOS")),
):
    query = db.query(Curso)
    if estado != "TODOS":
        query = query.filter(Curso.estado == estado)
    return query.offset(offset).limit(limit).all()

@router.post("/")
def crear_curso(
    curso_in: dict,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_role_and_view({"admin"}, "CURSOS")),
):
    estado = curso_in.get("estado")
    if estado is not None:
        estado_norm = str(estado).strip().upper()
        if estado_norm not in {"ACTIVO", "INACTIVO"}:
            raise HTTPException(status_code=400, detail="estado inválido")
        curso_in["estado"] = estado_norm
    c = Curso(**curso_in)
    db.add(c); db.commit(); db.refresh(c)
    return c

@router.post("/{curso_id}/paralelos")
def crear_paralelo(
    curso_id:int,
    data:dict,
    db:Session=Depends(get_db),
    _: Usuario = Depends(require_role_and_view({"admin"}, "CURSOS")),
):
    if not db.get(Curso, curso_id): raise HTTPException(404, "Curso no encontrado")
    estado = data.get("estado")
    if estado is not None:
        estado_norm = str(estado).strip().upper()
        if estado_norm not in {"ACTIVO", "INACTIVO"}:
            raise HTTPException(status_code=400, detail="estado inválido")
        data["estado"] = estado_norm
    p = Paralelo(curso_id=curso_id, **data); db.add(p); db.commit(); db.refresh(p); return p
