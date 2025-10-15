"""Tests for the permission cache helpers."""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.permissions import permission_cache
from app.db import models
from app.db.base import Base


def test_permissions_are_normalised_to_uppercase():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, future=True)

    try:
        with SessionLocal() as session:  # type: Session
            rol = models.Rol(nombre="Admin", codigo="ADMIN")
            vista = models.Vista(nombre="Personas", codigo="personas")
            session.add_all([rol, vista])
            session.flush()
            session.execute(
                models.rol_vistas.insert().values(rol_id=rol.id, vista_id=vista.id)
            )
            session.commit()

            permisos = permission_cache.get_permissions(session, rol.id)
            assert permisos == {"PERSONAS"}

            # Ensure the cached value remains normalised.
            vista.codigo = "alumnos"
            session.commit()
            cached = permission_cache.get_permissions(session, rol.id)
            assert cached == {"PERSONAS"}
    finally:
        permission_cache.clear()
        Base.metadata.drop_all(engine)
        engine.dispose()


def test_permissions_are_trimmed_before_caching():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, future=True)

    try:
        with SessionLocal() as session:  # type: Session
            rol = models.Rol(nombre="Docente", codigo="DOCENTE")
            vista = models.Vista(nombre="Estudiantes", codigo="  estudiantes  ")
            session.add_all([rol, vista])
            session.flush()
            session.execute(
                models.rol_vistas.insert().values(rol_id=rol.id, vista_id=vista.id)
            )
            session.commit()

            permisos = permission_cache.get_permissions(session, rol.id)
            assert permisos == {"ESTUDIANTES"}
    finally:
        permission_cache.clear()
        Base.metadata.drop_all(engine)
        engine.dispose()

