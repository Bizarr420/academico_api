import sys
import types
from datetime import date
from pathlib import Path

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Provide a lightweight stub for ``mysql.connector`` so importing the API modules
# does not require the optional MySQL dependency during the tests.
mysql_module = types.ModuleType("mysql")
connector_module = types.ModuleType("mysql.connector")
connector_module.apilevel = "2.0"
connector_module.threadsafety = 1
connector_module.paramstyle = "pyformat"


def _mysql_connect(*args, **kwargs):  # pragma: no cover - defensive stub
    raise RuntimeError("mysql connector is not available in the test environment")


connector_module.connect = _mysql_connect
mysql_module.connector = connector_module
sys.modules.setdefault("mysql", mysql_module)
sys.modules.setdefault("mysql.connector", connector_module)

from app.api.v1.docentes import crear_docente
from app.api.v1.estudiantes import crear_estudiante
from app.db import models
from app.db.base import Base
from app.schemas.docentes import DocenteCreate
from app.schemas.estudiantes import EstudianteCreate
from app.schemas.personas import PersonaCreate


def create_test_engine():
    return create_engine("sqlite+pysqlite:///:memory:", future=True)


@pytest.fixture
def db_session():
    engine = create_test_engine()
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


def build_persona_payload(ci: str | None = None) -> PersonaCreate:
    return PersonaCreate(
        nombres="Ana",
        apellidos="Pérez",
        sexo=models.SexoEnum.FEMENINO,
        fecha_nacimiento=date(2000, 1, 1),
        celular="78945612",
        direccion="Av. Siempre Viva",
        ci_numero=ci,
        ci_complemento=None,
        ci_expedicion="LP" if ci else None,
    )


def test_crear_estudiante_con_persona_id(db_session):
    persona = models.Persona(
        nombres="Luis",
        apellidos="Torrez",
        sexo=models.SexoEnum.MASCULINO,
        fecha_nacimiento=date(1999, 5, 20),
    )
    db_session.add(persona)
    db_session.commit()

    payload = EstudianteCreate(persona_id=persona.id, codigo_est="EST-001")

    estudiante = crear_estudiante(payload, db_session)

    assert estudiante.id is not None
    assert estudiante.persona_id == persona.id
    assert estudiante.persona is not None
    assert estudiante.codigo_est == "EST-001"


def test_crear_estudiante_con_persona_nueva(db_session):
    payload = EstudianteCreate(persona=build_persona_payload(ci="CI-123"), codigo_est="EST-002")

    estudiante = crear_estudiante(payload, db_session)

    assert estudiante.persona is not None
    assert estudiante.persona.ci is not None
    assert estudiante.persona.ci.ci_numero == "CI-123"


def test_crear_estudiante_con_ci_duplicado(db_session):
    crear_estudiante(
        EstudianteCreate(persona=build_persona_payload(ci="CI-777"), codigo_est="EST-100"),
        db_session,
    )

    with pytest.raises(HTTPException) as excinfo:
        crear_estudiante(
            EstudianteCreate(persona=build_persona_payload(ci="CI-777"), codigo_est="EST-101"),
            db_session,
        )

    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "CI ya registrado"


def test_crear_docente_con_persona_id(db_session):
    persona = models.Persona(
        nombres="Rosa",
        apellidos="García",
        sexo=models.SexoEnum.FEMENINO,
        fecha_nacimiento=date(1985, 8, 12),
    )
    db_session.add(persona)
    db_session.commit()

    payload = DocenteCreate(persona_id=persona.id, titulo="Lic.", profesion="Educación")

    docente = crear_docente(payload, db_session, None)

    assert docente.id is not None
    assert docente.persona_id == persona.id
    assert docente.persona is not None
    assert docente.titulo == "Lic."


def test_crear_docente_con_persona_nueva(db_session):
    payload = DocenteCreate(persona=build_persona_payload(ci="CI-888"), titulo="Ing.")

    docente = crear_docente(payload, db_session, None)

    assert docente.persona is not None
    assert docente.persona.ci is not None
    assert docente.persona.ci.ci_numero == "CI-888"


def test_crear_docente_con_ci_duplicado(db_session):
    crear_estudiante(
        EstudianteCreate(persona=build_persona_payload(ci="CI-999"), codigo_est="EST-200"),
        db_session,
    )

    with pytest.raises(HTTPException) as excinfo:
        crear_docente(
            DocenteCreate(persona=build_persona_payload(ci="CI-999"), titulo="Lic."),
            db_session,
            None,
        )

    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "CI ya registrado"
