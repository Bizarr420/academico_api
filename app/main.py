"""Application entry-point for Académico API."""

from __future__ import annotations

from datetime import date
from typing import Final

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.api.v1.router import api_router
from app.core.security import hash_password
from app.db.models import (
    EstadoUsuarioEnum,
    Persona,
    Rol,
    SexoEnum,
    Usuario,
    Vista,
)
from app.db.session import engine


app = FastAPI(title="Académico API")


DEFAULT_VISTAS: Final[dict[str, str]] = {
    "USUARIOS": "Usuarios",
    "ROLES": "Roles",
    "VISTAS": "Vistas",
    "PLANES": "Planes de estudio",
    "GESTIONES": "Gestiones",
    "NIVELES": "Niveles",
    "DOCENTES": "Docentes",
    "ASISTENCIAS": "Asistencias",
    "CURSOS": "Cursos",
    "ALERTAS": "Alertas",
    "NOTAS": "Notas",
    "MATERIAS": "Materias",
    "REPORTES": "Reportes",
    "PARALELOS": "Paralelos",
    "ASIGNACIONES": "Asignaciones",
    "MATRICULAS": "Matrículas",
    "AUDITORIA": "Auditoría",
}

ROLE_TEMPLATES: Final[tuple[dict[str, object], ...]] = (
    {
        "nombre": "Administrador",
        "codigo": "ADMIN",
        "vista_codes": tuple(DEFAULT_VISTAS.keys()),
    },
    {
        "nombre": "Docente",
        "codigo": "DOC",
        "vista_codes": (
            "ASISTENCIAS",
            "NOTAS",
            "CURSOS",
            "MATERIAS",
            "ASIGNACIONES",
            "REPORTES",
            "ALERTAS",
        ),
    },
    {
        "nombre": "Padre de familia",
        "codigo": "PAD",
        "vista_codes": (
            "ASISTENCIAS",
            "NOTAS",
            "REPORTES",
            "ALERTAS",
        ),
    },
)

SUPERUSER_USERNAME: Final[str] = "root"
SUPERUSER_PASSWORD: Final[str] = "CambiarAhora123!"
SUPERUSER_NAMES: Final[str] = "Súper"
SUPERUSER_LASTNAMES: Final[str] = "Administrador"
SUPERUSER_BIRTHDATE: Final[date] = date(1980, 1, 1)


@app.on_event("startup")
def bootstrap_access_control() -> None:
    """Synchronise vistas, roles and privileged users with the database."""

    with Session(engine) as session:
        vistas_by_code: dict[str, Vista] = {
            vista.codigo.upper(): vista for vista in session.query(Vista).all()
        }

        for code, name in DEFAULT_VISTAS.items():
            vista = vistas_by_code.get(code)
            if vista is None:
                vista = Vista(nombre=name, codigo=code)
                session.add(vista)
                session.flush()
                vistas_by_code[code] = vista
            else:
                updated = False
                if vista.nombre != name:
                    vista.nombre = name
                    updated = True
                if vista.codigo != code:
                    vista.codigo = code
                    updated = True
                if updated:
                    session.add(vista)
                vistas_by_code[code] = vista

        session.flush()

        for template in ROLE_TEMPLATES:
            codigo = template["codigo"]
            vista_codes = tuple(template["vista_codes"])
            vistas = [vistas_by_code[view_code] for view_code in vista_codes]

            rol: Rol | None = (
                session.query(Rol)
                .options(selectinload(Rol.vistas))
                .filter(func.upper(Rol.codigo) == codigo)
                .first()
            )
            if rol is None:
                rol = Rol(nombre=template["nombre"], codigo=codigo)
                session.add(rol)
                session.flush()
            else:
                rol.nombre = template["nombre"]
                rol.codigo = codigo

            rol.vistas = vistas
            session.add(rol)

        session.flush()

        admin_role: Rol | None = (
            session.query(Rol)
            .filter(func.upper(Rol.codigo) == "ADMIN")
            .first()
        )

        if admin_role is not None:
            admin_user = (
                session.query(Usuario)
                .filter(func.lower(Usuario.username) == "admin")
                .first()
            )
            if admin_user is not None and admin_user.rol_id != admin_role.id:
                admin_user.rol = admin_role

            superuser = (
                session.query(Usuario)
                .filter(func.lower(Usuario.username) == SUPERUSER_USERNAME.lower())
                .first()
            )
            if superuser is None:
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

                superuser = Usuario(
                    persona=persona,
                    username=SUPERUSER_USERNAME,
                    password_hash=hash_password(SUPERUSER_PASSWORD),
                    rol=admin_role,
                    estado=EstadoUsuarioEnum.ACTIVO,
                )
                session.add(superuser)
            elif superuser.rol_id != admin_role.id:
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
