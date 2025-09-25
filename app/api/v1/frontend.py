from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db import models
from app.schemas.docentes import DocenteCreate
from app.schemas.estudiantes import EstudianteCreate
from app.schemas.frontend import (
    PaginatedStudents,
    PaginatedTeachers,
    StudentItem,
    TeacherItem,
)
from app.schemas.personas import PersonaOut


router = APIRouter(tags=["frontend-compat"])


def _build_persona(persona: models.Persona) -> PersonaOut:
    return PersonaOut.model_validate(persona, from_attributes=True)


@router.get("/students", response_model=PaginatedStudents)
def listar_estudiantes(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = Query(default=None, min_length=1),
):
    query = (
        db.query(models.Estudiante, models.Persona)
        .join(models.Persona, models.Persona.id == models.Estudiante.persona_id)
    )

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(
                models.Persona.nombres.ilike(pattern),
                models.Persona.apellidos.ilike(pattern),
                models.Estudiante.codigo_est.ilike(pattern),
            )
        )

    total = query.with_entities(func.count(models.Estudiante.id)).scalar() or 0
    offset = (page - 1) * page_size
    rows = query.order_by(models.Estudiante.id).offset(offset).limit(page_size).all()

    items = [
        StudentItem(
            id=est.id,
            persona_id=est.persona_id,
            codigo_est=est.codigo_est,
            persona=_build_persona(persona),
        )
        for est, persona in rows
    ]

    return PaginatedStudents(items=items, total=total, page=page, page_size=page_size)


@router.post("/students", response_model=StudentItem, status_code=status.HTTP_201_CREATED)
def crear_estudiante(payload: EstudianteCreate, db: Session = Depends(get_db)):
    persona = db.get(models.Persona, payload.persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    existe = (
        db.query(models.Estudiante)
        .filter(models.Estudiante.codigo_est == payload.codigo_est)
        .first()
    )
    if existe:
        raise HTTPException(status_code=400, detail="codigo_est ya existe")

    est = models.Estudiante(persona_id=payload.persona_id, codigo_est=payload.codigo_est)
    db.add(est)
    db.commit()
    db.refresh(est)
    persona = db.get(models.Persona, est.persona_id)

    return StudentItem(
        id=est.id,
        persona_id=est.persona_id,
        codigo_est=est.codigo_est,
        persona=_build_persona(persona),
    )


@router.get("/teachers", response_model=PaginatedTeachers)
def listar_docentes(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = Query(default=None, min_length=1),
):
    query = (
        db.query(models.Docente, models.Persona)
        .join(models.Persona, models.Persona.id == models.Docente.persona_id)
    )

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(
                models.Persona.nombres.ilike(pattern),
                models.Persona.apellidos.ilike(pattern),
                models.Docente.titulo.ilike(pattern),
            )
        )

    total = query.with_entities(func.count(models.Docente.id)).scalar() or 0
    offset = (page - 1) * page_size
    rows = query.order_by(models.Docente.id).offset(offset).limit(page_size).all()

    items = [
        TeacherItem(
            id=doc.id,
            persona_id=doc.persona_id,
            titulo=doc.titulo,
            persona=_build_persona(persona),
        )
        for doc, persona in rows
    ]

    return PaginatedTeachers(items=items, total=total, page=page, page_size=page_size)


@router.post("/teachers", response_model=TeacherItem, status_code=status.HTTP_201_CREATED)
def crear_docente(payload: DocenteCreate, db: Session = Depends(get_db)):
    persona = db.get(models.Persona, payload.persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    existente = (
        db.query(models.Docente)
        .filter(models.Docente.persona_id == payload.persona_id)
        .first()
    )
    if existente:
        raise HTTPException(status_code=400, detail="persona_id ya está asignado a un docente")

    docente = models.Docente(persona_id=payload.persona_id, titulo=payload.titulo)
    db.add(docente)
    db.commit()
    db.refresh(docente)
    persona = db.get(models.Persona, docente.persona_id)

    return TeacherItem(
        id=docente.id,
        persona_id=docente.persona_id,
        titulo=docente.titulo,
        persona=_build_persona(persona),
    )
