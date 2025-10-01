import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import models
from app.schemas.docentes import DocenteOut
from app.schemas.estudiantes import EstudianteOut


def test_estudiante_out_accepts_orm_objects():
    persona = models.Persona(
        id=2,
        nombres="Ana",
        apellidos="Pérez",
        sexo=models.SexoEnum.FEMENINO,
        fecha_nacimiento=date(2000, 1, 1),
    )
    estudiante = models.Estudiante(
        id=1,
        persona_id=persona.id,
        codigo_est="ABC123",
        anio_ingreso=2024,
        situacion=models.SituacionEstudianteEnum.REGULAR.value,
        estado=models.EstadoEstudianteEnum.ACTIVO.value,
    )
    estudiante.persona = persona

    schema = EstudianteOut.model_validate(estudiante)

    assert schema.id == 1
    assert schema.persona_id == 2
    assert schema.codigo_est == "ABC123"
    assert schema.anio_ingreso == 2024
    assert schema.situacion == models.SituacionEstudianteEnum.REGULAR
    assert schema.estado == models.EstadoEstudianteEnum.ACTIVO
    assert schema.persona is not None
    assert schema.persona.id == persona.id


def test_docente_out_accepts_orm_objects():
    persona = models.Persona(
        id=3,
        nombres="Juan",
        apellidos="Suárez",
        sexo=models.SexoEnum.MASCULINO,
        fecha_nacimiento=date(1995, 7, 1),
    )
    docente = models.Docente(
        id=7,
        persona_id=persona.id,
        titulo="Lic.",
        profesion="Educación",
    )
    docente.persona = persona

    schema = DocenteOut.model_validate(docente)

    assert schema.id == 7
    assert schema.persona_id == 3
    assert schema.titulo == "Lic."
    assert schema.profesion == "Educación"
    assert schema.persona is not None
    assert schema.persona.id == persona.id
