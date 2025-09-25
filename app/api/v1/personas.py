# app/api/v1/personas.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.db.models import Persona, CIPersona
from app.schemas.personas import PersonaCreate, PersonaOut

router = APIRouter()

@router.post("/", response_model=PersonaOut)   # 👈 sin get_current_user aquí
def crear_persona(data: PersonaCreate, db: Session = Depends(get_db)):
    persona = Persona(
        nombres=data.nombres,
        apellidos=data.apellidos,
        sexo=data.sexo,
        fecha_nacimiento=data.fecha_nacimiento,
        celular=data.celular,
        direccion=data.direccion,
    )
    db.add(persona)
    db.flush()
    if data.ci_numero:
        if db.query(CIPersona).filter(CIPersona.ci_numero == data.ci_numero).first():
            raise HTTPException(status_code=400, detail="CI ya registrado")
        db.add(CIPersona(
            persona_id=persona.id,
            ci_numero=data.ci_numero,
            ci_complemento=data.ci_complemento,
            ci_expedicion=data.ci_expedicion
        ))
    db.commit()
    db.refresh(persona)
    return persona
