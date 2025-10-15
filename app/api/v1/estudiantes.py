from datetime import date
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_db
from app.api.deps_extra import require_view
from app.db import models
from app.db.models import Usuario
from app.schemas.estudiantes import EstudianteCreate, EstudianteOut
from app.services.personas import create_persona

router = APIRouter(tags=["estudiantes"])

@router.post("/", response_model=EstudianteOut, status_code=201)
def crear_estudiante(
    payload: EstudianteCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("ESTUDIANTES")),
):
    codigo_rude = payload.codigo_rude.strip()
    if not codigo_rude:
        raise HTTPException(status_code=400, detail="codigo_rude es requerido")

    ingreso = payload.anio_ingreso or date.today().year
    situacion = (
        payload.situacion.value if hasattr(payload.situacion, "value") else payload.situacion
    )
    estado = payload.estado.value if hasattr(payload.estado, "value") else payload.estado

    if payload.persona is not None:
        try:
            persona = create_persona(db, payload.persona)
            _ensure_codigo_rude_available(db, codigo_rude)

            est = models.Estudiante(
                persona_id=persona.id,
                codigo_rude=codigo_rude,
                anio_ingreso=ingreso,
                situacion=situacion,
                estado=estado,
            )
            db.add(est)
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise _translate_integrity_error(exc)
        except Exception:
            db.rollback()
            raise

        db.refresh(est)
        db.refresh(est, attribute_names=["persona"])
        return est

    persona = db.get(models.Persona, payload.persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    _ensure_codigo_rude_available(db, codigo_rude)
    _ensure_persona_available(db, payload.persona_id)

    est = models.Estudiante(persona_id=payload.persona_id, codigo_rude=codigo_rude)
    est.anio_ingreso = ingreso
    est.situacion = situacion
    est.estado = estado
    db.add(est)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise _translate_integrity_error(exc)

    db.refresh(est)
    db.refresh(est, attribute_names=["persona"])

    return est


def _ensure_codigo_rude_available(db: Session, codigo_rude: str) -> None:
    existe = (
        db.query(models.Estudiante.id)
        .filter(models.Estudiante.codigo_rude == codigo_rude)
        .first()
    )
    if existe:
        raise HTTPException(status_code=400, detail="codigo_rude ya existe")


def _ensure_persona_available(db: Session, persona_id: int | None) -> None:
    if persona_id is None:
        return
    existe = (
        db.query(models.Estudiante.id)
        .filter(models.Estudiante.persona_id == persona_id)
        .first()
    )
    if existe:
        raise HTTPException(
            status_code=400,
            detail="La persona ya está registrada como estudiante",
        )


def _translate_integrity_error(exc: IntegrityError) -> HTTPException:
    raw_message = str(getattr(exc.orig, "args", [exc])[0]).lower()
    if "uq_estudiantes_persona" in raw_message or "persona" in raw_message and "unique" in raw_message:
        return HTTPException(
            status_code=400,
            detail="La persona ya está registrada como estudiante",
        )
    if "uq_estudiantes_rude" in raw_message or "codigo" in raw_message and "rude" in raw_message:
        return HTTPException(status_code=400, detail="codigo_rude ya existe")
    return HTTPException(status_code=400, detail="No se pudo registrar al estudiante")


@router.get("/", response_model=List[EstudianteOut])
def listar_estudiantes(
    db: Session = Depends(get_db),
    persona_id: Optional[int] = Query(None, gt=0),
    codigo_rude: Optional[str] = Query(None, min_length=1),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=500),
    estado: Literal["ACTIVO", "INACTIVO", "TODOS"] = Query("ACTIVO"),
    _: Usuario = Depends(require_view("ESTUDIANTES")),
):
    q = db.query(models.Estudiante).options(selectinload(models.Estudiante.persona))
    if persona_id:
        q = q.filter(models.Estudiante.persona_id == persona_id)
    if codigo_rude:
        q = q.filter(models.Estudiante.codigo_rude == codigo_rude)
    if estado != "TODOS":
        q = q.filter(models.Estudiante.estado == estado)

    effective_limit = page_size if page_size is not None else limit
    if page is not None:
        effective_offset = (page - 1) * effective_limit
    else:
        effective_offset = offset

    return q.offset(effective_offset).limit(effective_limit).all()

@router.get("/{estudiante_id}", response_model=EstudianteOut)
def obtener_estudiante(
    estudiante_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("ESTUDIANTES")),
):
    est = db.get(models.Estudiante, estudiante_id)
    if not est:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return est
