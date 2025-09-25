from sqlalchemy import text
from app.db.base import Base
from app.db.session import engine
import app.db.models
from fastapi import FastAPI
from app.api.v1.router import api_router
from app.db import models
from app.db import models  # 👈 importa modelos, sin crear un nombre 'app' paquete aquí

from fastapi import FastAPI
from sqlalchemy import text
from app.db.session import engine
from app.db.base import Base
from app.db import models  # importa modelos sin crear el nombre 'app' en este módulo

app = FastAPI(title="Académico API")

# ✅ Usamos Alembic; NO llames create_all()
@app.on_event("startup")
def on_startup():
    with engine.begin() as conn:
        conn.execute(text("INSERT IGNORE INTO roles (nombre) VALUES ('ADMIN'), ('DOCENTE')"))

from app.api.v1.router import api_router
app.include_router(api_router, prefix="/api/v1")

from fastapi.middleware.cors import CORSMiddleware
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.routing import APIRoute

@app.on_event("startup")
def log_routes():
    print("=== RUTAS ===")
    for r in app.routes:
        if isinstance(r, APIRoute):
            print(f"{list(r.methods)} {r.path}")

