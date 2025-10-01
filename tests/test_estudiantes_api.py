import sys
import types
from datetime import date
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Stub optional MySQL dependency expected by the application modules.
mysql_module = types.ModuleType("mysql")
connector_module = types.ModuleType("mysql.connector")
connector_module.apilevel = "2.0"
connector_module.threadsafety = 1
connector_module.paramstyle = "pyformat"
connector_module.Error = RuntimeError
connector_module.OperationalError = RuntimeError
connector_module.InterfaceError = RuntimeError


def _mysql_connect(*args, **kwargs):  # pragma: no cover - defensive stub
    raise RuntimeError("mysql connector is not available in the test environment")


connector_module.connect = _mysql_connect
mysql_module.connector = connector_module
sys.modules.setdefault("mysql", mysql_module)
sys.modules.setdefault("mysql.connector", connector_module)

from app.api.deps import get_db
from app.db import models
from app.db.base import Base
from app.main import app


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(
        bind=engine, autoflush=False, autocommit=False, future=True
    )

    def override_get_db():
        session = TestingSession()
        try:
            yield session
            session.commit()
        finally:
            session.close()

    original_startup = list(app.router.on_startup)
    original_shutdown = list(app.router.on_shutdown)
    app.router.on_startup.clear()
    app.router.on_shutdown.clear()
    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.router.on_startup.clear()
        app.router.on_startup.extend(original_startup)
        app.router.on_shutdown.clear()
        app.router.on_shutdown.extend(original_shutdown)
        Base.metadata.drop_all(engine)
        engine.dispose()


def test_crear_estudiante_con_codigo_valido(client):
    payload = {
        "codigo_rude": "RUDE-500",
        "persona": {
            "nombres": "Laura",
            "apellidos": "Mendoza",
            "sexo": models.SexoEnum.FEMENINO.value,
            "fecha_nacimiento": date(2004, 6, 15).isoformat(),
            "celular": "71234567",
            "direccion": "Av. Central",
            "ci_numero": "CI-500",
            "ci_expedicion": "LP",
        },
    }

    response = client.post("/api/v1/estudiantes/", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["codigo_rude"] == "RUDE-500"
    assert body["persona_id"] > 0
    assert body["persona"]["nombres"] == "Laura"
    assert body["persona"]["sexo"] == models.SexoEnum.FEMENINO.short_code
    assert body["anio_ingreso"] == date.today().year
    assert body["situacion"] == "REGULAR"
    assert body["estado"] == "ACTIVO"


def test_crear_estudiante_sin_codigo_retorna_400(client):
    payload = {
        "codigo_rude": "   ",
        "persona": {
            "nombres": "Mario",
            "apellidos": "Gutiérrez",
            "sexo": models.SexoEnum.MASCULINO.value,
            "fecha_nacimiento": date(2003, 3, 10).isoformat(),
        },
    }

    response = client.post("/api/v1/estudiantes/", json=payload)

    assert response.status_code == 400
    assert response.json() == {"detail": "codigo_rude es requerido"}
