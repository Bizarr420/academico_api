from fastapi import APIRouter

# IMPORTA EXPLÍCITAMENTE el router de materias con alias
from .materias import router as materias_router

from . import (
    alertas,
    asistencia,
    asignaciones,
    auth,
    docentes,
    cursos,
    evaluaciones,
    estudiantes,
    frontend,
    gestiones,
    matriculas,
    niveles,
    notas,
    paralelos,
    personas,
    planes,
    reportes,
    roles,
    usuarios,
)

api_router = APIRouter()
api_router.include_router(auth.router,         prefix="/auth",         tags=["auth"])
api_router.include_router(personas.router,     prefix="/personas",     tags=["personas"])
api_router.include_router(estudiantes.router,  prefix="/estudiantes",  tags=["estudiantes"])
api_router.include_router(notas.router,        prefix="/notas",        tags=["notas"])
api_router.include_router(evaluaciones.router, prefix="/evaluaciones", tags=["evaluaciones"])
api_router.include_router(cursos.router,       prefix="/cursos",       tags=["cursos"])
api_router.include_router(paralelos.router,    prefix="/paralelos",    tags=["paralelos"])
api_router.include_router(niveles.router,      prefix="/niveles",      tags=["niveles"])
api_router.include_router(gestiones.router,    prefix="/gestiones",    tags=["gestiones"])
api_router.include_router(docentes.router,     prefix="/docentes",     tags=["docentes"])
api_router.include_router(usuarios.router,     prefix="/usuarios",     tags=["usuarios"])
api_router.include_router(roles.router,        prefix="/roles",        tags=["roles"])
api_router.include_router(planes.router,       prefix="/planes",       tags=["planes"])

# 🔐 usa el alias explícito (evita choques con app.schemas.materias)
api_router.include_router(materias_router)

api_router.include_router(asistencia.router,   prefix="/asistencias",  tags=["asistencias"])
api_router.include_router(asignaciones.router, prefix="/asignaciones", tags=["asignaciones"])
api_router.include_router(matriculas.router,   prefix="/matriculas",   tags=["matriculas"])
api_router.include_router(reportes.router,     prefix="/reportes",     tags=["reportes"])
api_router.include_router(alertas.router, prefix="/alertas", tags=["alertas"])
api_router.include_router(frontend.router)
