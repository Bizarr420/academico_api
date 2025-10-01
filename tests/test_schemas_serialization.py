import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import models
from app.schemas.docentes import DocenteOut
from app.schemas.estudiantes import EstudianteOut


def test_estudiante_out_accepts_orm_objects():
    estudiante = models.Estudiante(id=1, persona_id=2, codigo_est="ABC123")

    schema = EstudianteOut.model_validate(estudiante)

    assert schema.id == 1
    assert schema.persona_id == 2
    assert schema.codigo_est == "ABC123"


def test_docente_out_accepts_orm_objects():
    docente = models.Docente(
        id=7,
        persona_id=3,
        titulo="Lic.",
        profesion="Educación",
    )

    schema = DocenteOut.model_validate(docente)

    assert schema.id == 7
    assert schema.persona_id == 3
    assert schema.titulo == "Lic."
    assert schema.profesion == "Educación"
