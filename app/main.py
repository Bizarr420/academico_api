"""Application entry-point for Académico API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.router import api_router
from app.db.models import Rol
from app.db.session import engine


app = FastAPI(title="Académico API")


@app.on_event("startup")
def seed_roles() -> None:
    """Ensure that the default roles exist in the database."""
    desired_roles = {"ADMIN", "DOCENTE"}

    with Session(engine) as session:
        existing = {nombre for (nombre,) in session.execute(select(Rol.nombre))}
        missing = desired_roles - existing
        if not missing:
            return

        session.add_all([Rol(nombre=nombre) for nombre in sorted(missing)])
        session.commit()


app.include_router(api_router, prefix="/api/v1")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
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
