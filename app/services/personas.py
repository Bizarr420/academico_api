"""Helpers for working with personas within transactional flows."""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models import CIPersona, Persona
from app.schemas.personas import PersonaCreate


def create_persona(db: Session, data: PersonaCreate) -> Persona:
    """Create a :class:`Persona` and its CI record when provided.

    The function mirrors the behaviour of the ``/personas`` endpoint so it can be
    reused by other routes that need to create a ``Persona`` as part of a wider
    transaction.
    """

    if data.ci_numero:
        existe_ci = db.query(CIPersona).filter(CIPersona.ci_numero == data.ci_numero).first()
        if existe_ci:
            raise HTTPException(status_code=400, detail="CI ya registrado")

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
        db.add(
            CIPersona(
                persona_id=persona.id,
                ci_numero=data.ci_numero,
                ci_complemento=data.ci_complemento,
                ci_expedicion=data.ci_expedicion,
            )
        )

    return persona
