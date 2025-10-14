"""Application entry-point for Académico API."""

from __future__ import annotations

from datetime import date
from typing import Final

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from sqlalchemy import func, inspect, text
from sqlalchemy.orm import Session, load_only

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.security import hash_password
from app.db.models import EstadoUsuarioEnum, Persona, Rol, SexoEnum, Usuario
from app.db.session import engine


app = FastAPI(title="Académico API")


SUPERUSER_USERNAME: Final[str] = "root"
SUPERUSER_PASSWORD: Final[str] = "CambiarAhora123!"
SUPERUSER_NAMES: Final[str] = "Súper"
SUPERUSER_LASTNAMES: Final[str] = "Administrador"
SUPERUSER_BIRTHDATE: Final[date] = date(1980, 1, 1)


def _ensure_roles_estado_column() -> None:
    """Make sure the ``roles`` table exposes the ``estado`` column.

    Some legacy deployments where migrations were not executed missed the
    ``estado`` column that newer application versions expect.  Instead of
    crashing on login (when the relationship is loaded) we opportunistically
    patch the schema at startup so the application can continue to operate.
    The logic mirrors the Alembic migration but runs defensively and is safe to
    execute multiple times.
    """

    with engine.begin() as connection:
        inspector = inspect(connection)
        columns = {column["name"]: column for column in inspector.get_columns("roles")}
        estado_info = columns.get("estado")

        if estado_info is None:
            connection.execute(
                text(
                    "ALTER TABLE roles ADD COLUMN estado VARCHAR(10)"
                    " DEFAULT 'ACTIVO'"
                )
            )
            connection.execute(text("UPDATE roles SET estado = 'ACTIVO' WHERE estado IS NULL"))
            connection.execute(
                text(
                    "ALTER TABLE roles MODIFY COLUMN estado VARCHAR(10)"
                    " NOT NULL DEFAULT 'ACTIVO'"
                )
            )
        else:
            connection.execute(text("UPDATE roles SET estado = 'ACTIVO' WHERE estado IS NULL"))
            if estado_info.get("nullable", True):
                connection.execute(
                    text(
                        "ALTER TABLE roles MODIFY COLUMN estado VARCHAR(10)"
                        " NOT NULL DEFAULT 'ACTIVO'"
                    )
                )


@app.on_event("startup")
def bootstrap_access_control() -> None:
    """Ensure a default superuser exists while role management is disabled."""

    _ensure_roles_estado_column()

    with Session(engine) as session:
        admin_role = (
            session.query(Rol)
            .options(load_only(Rol.id, Rol.nombre, Rol.codigo))
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
#app.include_router(api_router, prefix="/api/v1")
app.include_router(api_router, prefix="/api")


cors_allowed_origins = list(dict.fromkeys(settings.CORS_ALLOWED_ORIGINS))
if settings.FRONTEND_EC2_URL and settings.FRONTEND_EC2_URL not in cors_allowed_origins:
    cors_allowed_origins.append(settings.FRONTEND_EC2_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_allowed_origins,
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
