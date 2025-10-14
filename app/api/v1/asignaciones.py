from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.deps_extra import require_view
from app.db.models import (
    AsignacionDocente,
    Curso,
    Docente,
    Gestion,
    Materia,
    Paralelo,
    Usuario,
)
from app.schemas.asignaciones import AsignacionCreate, AsignacionOut

router = APIRouter(tags=["asignaciones"])

@router.post(
    "/",
    response_model=AsignacionOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_asignacion(
    payload: AsignacionCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("ASIGNACIONES")),
):
    data = payload.model_dump()
    estado = (data.pop("estado") or "ACTIVO").strip().upper()
    if estado not in {"ACTIVO", "INACTIVO"}:
        raise HTTPException(status_code=400, detail="estado inválido")

    gestion = db.get(Gestion, data["gestion_id"])
    if not gestion:
        raise HTTPException(status_code=404, detail="Gestión no encontrada")
    if getattr(gestion, "estado", "ACTIVO") != "ACTIVO":
        raise HTTPException(
            status_code=409,
            detail={
                "error": "gestion_inactiva",
                "mensaje": "La gestión está inactiva",
                "gestion_id": gestion.id,
            },
        )

    docente = db.get(Docente, data["docente_id"])
    if not docente:
        raise HTTPException(status_code=404, detail="Docente no encontrado")
    if getattr(docente, "estado", "ACTIVO") != "ACTIVO":
        raise HTTPException(
            status_code=409,
            detail={
                "error": "docente_inactivo",
                "mensaje": "El docente está inactivo",
                "docente_id": docente.id,
            },
        )

    materia = db.get(Materia, data["materia_id"])
    if not materia:
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    if getattr(materia, "estado", "ACTIVO") != "ACTIVO":
        raise HTTPException(
            status_code=409,
            detail={
                "error": "materia_inactiva",
                "mensaje": "La materia está inactiva",
                "materia_id": materia.id,
            },
        )

    curso = db.get(Curso, data["curso_id"])
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    if getattr(curso, "estado", "ACTIVO") != "ACTIVO":
        raise HTTPException(
            status_code=409,
            detail={
                "error": "curso_inactivo",
                "mensaje": "El curso está inactivo",
                "curso_id": curso.id,
            },
        )

    paralelo = db.get(Paralelo, data["paralelo_id"])
    if not paralelo:
        raise HTTPException(status_code=404, detail="Paralelo no encontrado")
    if getattr(paralelo, "estado", "ACTIVO") != "ACTIVO":
        raise HTTPException(
            status_code=409,
            detail={
                "error": "paralelo_inactivo",
                "mensaje": "El paralelo está inactivo",
                "paralelo_id": paralelo.id,
            },
        )

    existe = db.query(AsignacionDocente).filter_by(**data).first()
    if existe:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "asignacion_duplicada",
                "mensaje": "La asignación ya existe",
                "asignacion_id": existe.id,
                "estado": existe.estado,
            },
        )

    asignacion = AsignacionDocente(**data, estado=estado)
    db.add(asignacion)
    db.commit()
    db.refresh(asignacion)
    return asignacion


@router.get("/", response_model=list[AsignacionOut])
def listar_asignaciones(
    gestion_id: int | None = Query(default=None, gt=0),
    gestion: str | None = Query(default=None),
    docente_id: int | None = Query(default=None, gt=0),
    curso_id: int | None = Query(default=None, gt=0),
    paralelo_id: int | None = Query(default=None, gt=0),
    materia_id: int | None = Query(default=None, gt=0),
    estado: Literal["ACTIVO", "INACTIVO", "TODOS"] = Query("ACTIVO"),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("ASIGNACIONES")),
):
    q = db.query(AsignacionDocente)
    if gestion_id is not None:
        q = q.filter(AsignacionDocente.gestion_id == gestion_id)
    elif gestion is not None:
        q = q.join(Gestion, Gestion.id == AsignacionDocente.gestion_id).filter(
            Gestion.nombre == gestion
        )
    if docente_id is not None:
        q = q.filter(AsignacionDocente.docente_id == docente_id)
    if curso_id is not None:
        q = q.filter(AsignacionDocente.curso_id == curso_id)
    if paralelo_id is not None:
        q = q.filter(AsignacionDocente.paralelo_id == paralelo_id)
    if materia_id is not None:
        q = q.filter(AsignacionDocente.materia_id == materia_id)
    if estado != "TODOS":
        q = q.filter(AsignacionDocente.estado == estado)
    return q.order_by(AsignacionDocente.id.asc()).all()


@router.delete("/{asignacion_id}", status_code=status.HTTP_200_OK)
def desactivar_asignacion(
    asignacion_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("ASIGNACIONES")),
):
    asignacion = db.get(AsignacionDocente, asignacion_id)
    if not asignacion:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")

    if asignacion.estado == "INACTIVO":
        return {"ok": True, "mensaje": "Asignación ya estaba inactiva"}

    asignacion.estado = "INACTIVO"
    db.commit()
    db.refresh(asignacion)
    return {"ok": True, "asignacion_id": asignacion.id, "estado": asignacion.estado}


@router.post("/{asignacion_id}/restore", response_model=AsignacionOut)
def restaurar_asignacion(
    asignacion_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("ASIGNACIONES")),
):
    asignacion = db.get(AsignacionDocente, asignacion_id)
    if not asignacion:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")

    asignacion.estado = "ACTIVO"
    db.commit()
    db.refresh(asignacion)
    return asignacion
