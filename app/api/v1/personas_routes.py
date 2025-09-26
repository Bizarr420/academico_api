from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import CIPersona, Persona, SexoEnum
from app.schemas.personas import PersonaCreate, PersonaOut


router = APIRouter()

@router.post("/", response_model=PersonaOut)
def crear_persona(data: PersonaCreate, db: Session = Depends(get_db)):
    p = Persona(
        nombres=data.nombres,
        apellidos=data.apellidos,
        sexo=SexoEnum(data.sexo),            # 👈 convierte "F" -> SexoEnum.F
        fecha_nacimiento=data.fecha_nacimiento,
        celular=data.celular,
        direccion=data.direccion,
    )
    db.add(p); db.flush()
    if data.ci_numero:
        if db.query(CIPersona).filter(CIPersona.ci_numero == data.ci_numero).first():
            raise HTTPException(status_code=400, detail="CI ya registrado")
        db.add(CIPersona(
            persona_id=p.id,
            ci_numero=data.ci_numero,
            ci_complemento=data.ci_complemento,
            ci_expedicion=data.ci_expedicion
        ))
    db.commit(); db.refresh(p)
    return p
@router.get("/{persona_id}", response_model=PersonaOut)
def obtener_persona(persona_id: int = Path(..., gt=0), db: Session = Depends(get_db)):
    p = db.get(Persona, persona_id)
    if not p:
        raise HTTPException(status_code=404, detail="No encontrado")
    return p

class PersonaUpdate(PersonaCreate):
    # todos opcionales para PATCH-like
    nombres: str | None = None
    apellidos: str | None = None
    sexo: str | None = None
    fecha_nacimiento: date | None = None

@router.put("/{persona_id}", response_model=PersonaOut)
def actualizar_persona(persona_id: int, data: PersonaUpdate, db: Session = Depends(get_db)):
    p = db.get(Persona, persona_id)
    if not p:
        raise HTTPException(status_code=404, detail="No encontrado")
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            if field == "sexo":
                setattr(p, field, SexoEnum(value))  # valida 'M','F','X'
            else:
                setattr(p, field, value)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p
