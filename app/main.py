"""Application entry-point for Académico API."""

from __future__ import annotations

from datetime import date
from typing import Final

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.v1.router import api_router
from app.core.security import hash_password
from app.db.models import EstadoUsuarioEnum, Persona, Rol, SexoEnum, Usuario
from app.db.session import engine


app = FastAPI(title="Académico API")


SUPERUSER_USERNAME: Final[str] = "root"
SUPERUSER_PASSWORD: Final[str] = "CambiarAhora123!"
SUPERUSER_NAMES: Final[str] = "Súper"
SUPERUSER_LASTNAMES: Final[str] = "Administrador"
SUPERUSER_BIRTHDATE: Final[date] = date(1980, 1, 1)


@app.on_event("startup")
def bootstrap_access_control() -> None:
    """Ensure a default superuser exists while role management is disabled."""

    with Session(engine) as session:
        admin_role = (
            session.query(Rol)
            .filter(func.lower(Rol.codigo) == "admin")
            .first()
        )
        if admin_role is None:
            admin_role = Rol(nombre="Administrador", codigo="ADMIN")
            session.add(admin_role)
            session.flush()

        persona = (
            session.query(Persona)
            .filter(
                func.lower(Persona.nombres) == SUPERUSER_NAMES.lower(),
                func.lower(Persona.apellidos) == SUPERUSER_LASTNAMES.lower(),
            )
            .first()
        )
        if persona is None:
            persona = Persona(
                nombres=SUPERUSER_NAMES,
                apellidos=SUPERUSER_LASTNAMES,
                sexo=SexoEnum.MASCULINO,
                fecha_nacimiento=SUPERUSER_BIRTHDATE,
            )
            session.add(persona)
            session.flush()

        superuser = (
            session.query(Usuario)
            .filter(func.lower(Usuario.username) == SUPERUSER_USERNAME.lower())
            .first()
        )
        if superuser is None:
            superuser = Usuario(
                persona=persona,
                username=SUPERUSER_USERNAME,
                password_hash=hash_password(SUPERUSER_PASSWORD),
                estado=EstadoUsuarioEnum.ACTIVO,
                rol=admin_role,
            )
            session.add(superuser)
        else:
            if superuser.persona_id != persona.id:
                superuser.persona = persona
            if superuser.estado != EstadoUsuarioEnum.ACTIVO:
                superuser.estado = EstadoUsuarioEnum.ACTIVO
            if superuser.rol_id != admin_role.id:
                superuser.rol = admin_role

        session.commit()


# Nota: la aplicación web espera actualmente que los endpoints vivan bajo
# ``/api`` mientras que la API estaba versionada en ``/api/v1``.  Esto
# provocaba errores 404 al autenticarse porque las solicitudes llegaban a
# ``/auth/login`` sin el prefijo de versión.  Para mantener compatibilidad con
# el frontend sin romper los clientes que ya usan ``/api/v1`` incluimos el
# router dos veces, otorgando un alias sin versión.
app.include_router(api_router, prefix="/api/v1")
app.include_router(api_router, prefix="/api")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def log_routes() -> None:
    """Print all registered API routes (useful for debugging)."""
    print("=== RUTAS ===")
    for route in app.routes:
        if isinstance(route, APIRoute):
            print(f"{sorted(route.methods)} {route.path}")
