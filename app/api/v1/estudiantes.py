from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api.deps import get_db
from app.db import models
from app.schemas.estudiantes import EstudianteCreate, EstudianteOut

router = APIRouter(tags=["estudiantes"])

@router.post("/", response_model=EstudianteOut, status_code=201)
def crear_estudiante(payload: EstudianteCreate, db: Session = Depends(get_db)):
    persona = db.get(models.Persona, payload.persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    existe = db.query(models.Estudiante).filter_by(codigo_est=payload.codigo_est).first()
    if existe:
        raise HTTPException(status_code=400, detail="codigo_est ya existe")

    est = models.Estudiante(persona_id=payload.persona_id, codigo_est=payload.codigo_est)
    db.add(est); db.commit(); db.refresh(est)
    return est

@router.get("/", response_model=List[EstudianteOut])
def listar_estudiantes(
    db: Session = Depends(get_db),
    persona_id: Optional[int] = Query(None, gt=0),
    codigo_est: Optional[str] = Query(None, min_length=1),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    q = db.query(models.Estudiante)
    if persona_id: q = q.filter(models.Estudiante.persona_id == persona_id)
    if codigo_est: q = q.filter(models.Estudiante.codigo_est == codigo_est)
    return q.offset(offset).limit(limit).all()

@router.get("/{estudiante_id}", response_model=EstudianteOut)
def obtener_estudiante(estudiante_id: int, db: Session = Depends(get_db)):
    est = db.get(models.Estudiante, estudiante_id)
    if not est:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return est
