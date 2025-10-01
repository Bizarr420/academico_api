# app/api/v1/personas.py
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.db.models import Persona
from app.schemas.personas import PersonaCreate, PersonaOut
from app.services.personas import create_persona

router = APIRouter()

@router.get("/", response_model=list[PersonaOut])
def listar_personas(db: Session = Depends(get_db)):
    personas = db.query(Persona).order_by(Persona.id).all()
    return personas


@router.get("/{persona_id}", response_model=PersonaOut)
def obtener_persona(persona_id: int = Path(..., gt=0), db: Session = Depends(get_db)):
    persona = db.get(Persona, persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return persona

@router.post("/", response_model=PersonaOut)   # 👈 sin get_current_user aquí
def crear_persona(data: PersonaCreate, db: Session = Depends(get_db)):
    persona = create_persona(db, data)
    db.commit()
    db.refresh(persona)
    return persona
