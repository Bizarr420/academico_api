"""Schemas for reporting endpoints."""

from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel


class SerieNota(BaseModel):
    evaluacion_id: int
    asignacion_id: int
    titulo: str
    fecha: date
    calificacion: float


class PromedioAsignacion(BaseModel):
    asignacion_id: int
    promedio: float
    evaluaciones: int


class TendenciaNotas(BaseModel):
    variacion: Optional[float]
    ultima: Optional[float]
    anterior: Optional[float]
    en_mejora: Optional[bool]


class EstudianteKPIs(BaseModel):
    promedio_general: Optional[float]
    evaluaciones_registradas: int
    mejor_nota: Optional[float]
    peor_nota: Optional[float]


class ReporteEstudianteOut(BaseModel):
    estudiante_id: int
    serie: list[SerieNota]
    por_asignacion: list[PromedioAsignacion]
    kpis: EstudianteKPIs
    tendencia: TendenciaNotas


class PromedioEstudiante(BaseModel):
    estudiante_id: int
    promedio: float


class SerieEvaluacion(BaseModel):
    evaluacion_id: int
    titulo: str
    fecha: date
    promedio: float


class CursoKPIs(BaseModel):
    promedio_general: Optional[float]
    estudiantes: int
    aprobados: int
    tasa_aprobacion: float
    mejor_promedio: Optional[PromedioEstudiante]
    peor_promedio: Optional[PromedioEstudiante]
    variacion_ultima_evaluacion: Optional[float]


class ReporteCursoOut(BaseModel):
    asignacion_id: int
    promedios_por_estudiante: list[PromedioEstudiante]
    serie_evaluaciones: list[SerieEvaluacion]
    kpis: CursoKPIs
