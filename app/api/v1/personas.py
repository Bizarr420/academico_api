# app/api/v1/personas.py
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.deps_extra import require_view
from app.db.models import Persona, Usuario
from app.schemas.personas import PersonaCreate, PersonaOut, PersonaUpdate

router = APIRouter()

@router.put("/{persona_id}", response_model=PersonaOut)
def actualizar_persona(
    persona_id: int,
    payload: PersonaUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("PERSONAS")),
):
    persona = db.get(Persona, persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        if value is not None:
            setattr(persona, field, value)
    db.add(persona)
    db.commit()
    db.refresh(persona)
    return persona

from app.services.personas import create_persona

@router.get("/", response_model=list[PersonaOut])
def listar_personas(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("PERSONAS")),
):
    personas = db.query(Persona).order_by(Persona.id).all()
    return personas


@router.get("/{persona_id}", response_model=PersonaOut)
def obtener_persona(
    persona_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("PERSONAS")),
):
    persona = db.get(Persona, persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return persona

@router.post("/", response_model=PersonaOut)
def crear_persona(
    data: PersonaCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("PERSONAS")),
):
    persona = create_persona(db, data)
    db.commit()
    db.refresh(persona)
    return persona
