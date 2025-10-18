
# ...existing code...

# app/api/v1/cursos.py
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query

def error_response(code: str, message: str, details: str | None = None, status_code: int = 400):
    return HTTPException(
        status_code=status_code,
        detail={
            "code": code,
            "message": message,
            "details": details,
        },
    )
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.deps_extra import require_role_and_view, require_view
from app.db.models import Curso, Paralelo, Usuario

router = APIRouter(tags=["cursos"])

@router.get("/{curso_id}")
def obtener_curso(
    curso_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("CURSOS")),
):
    from sqlalchemy.orm import selectinload
    curso = db.query(Curso).options(selectinload(Curso.paralelos)).filter(Curso.id == curso_id).first()
    if not curso:
        raise error_response(
            code="CURSO_NOT_FOUND",
            message="Curso no encontrado",
            details=f"No existe curso con id {curso_id}",
            status_code=404
        )
    return curso
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
    from sqlalchemy.orm import selectinload
    query = db.query(Curso).options(
        selectinload(Curso.paralelos),
        selectinload(Curso.nivel)
    )
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
            raise error_response(
                code="INVALID_ESTADO",
                message="Estado inválido",
                details=f"Valor recibido: {estado}",
                status_code=400
            )
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
    if not db.get(Curso, curso_id):
        raise error_response(
            code="CURSO_NOT_FOUND",
            message="Curso no encontrado",
            details=f"No existe curso con id {curso_id}",
            status_code=404
        )
    estado = data.get("estado")
    if estado is not None:
        estado_norm = str(estado).strip().upper()
        if estado_norm not in {"ACTIVO", "INACTIVO"}:
            raise error_response(
                code="INVALID_ESTADO",
                message="Estado inválido",
                details=f"Valor recibido: {estado}",
                status_code=400
            )
        data["estado"] = estado_norm
    p = Paralelo(curso_id=curso_id, **data); db.add(p); db.commit(); db.refresh(p); return p
