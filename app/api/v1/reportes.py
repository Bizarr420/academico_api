from datetime import date, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.deps_extra import require_view
from app.db.models import Evaluacion, Nota, Usuario
from app.schemas.reportes import (
    CursoKPIs,
    PromedioAsignacion,
    PromedioEstudiante,
    ReporteCursoOut,
    ReporteEstudianteOut,
    SerieEvaluacion,
    SerieNota,
    EstudianteKPIs,
    TendenciaNotas,
)

router = APIRouter(tags=["reportes"])


def _ensure_date(value: date | datetime | None) -> date:
    if value is None:
        return date.min
    if isinstance(value, datetime):
        return value.date()
    return value


@router.get(
    "/estudiante/{est_id}/notas",
    response_model=ReporteEstudianteOut,
)
def notas_estudiante(
    est_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("REPORTES")),
):
    rows = (
        db.query(
            Evaluacion.id,
            Evaluacion.asignacion_id,
            Evaluacion.titulo,
            Evaluacion.fecha,
            Nota.calificacion,
        )
        .join(Nota, Nota.evaluacion_id == Evaluacion.id)
        .filter(Nota.estudiante_id == est_id)
        .order_by(Evaluacion.fecha.asc(), Evaluacion.id.asc())
        .all()
    )

    serie: list[SerieNota] = []
    por_asignacion: dict[int, tuple[float, int]] = {}

    for eval_id, asignacion_id, titulo, fecha, calificacion in rows:
        fecha_val = _ensure_date(fecha)
        cal = float(calificacion)
        serie.append(
            SerieNota(
                evaluacion_id=int(eval_id),
                asignacion_id=int(asignacion_id),
                titulo=str(titulo),
                fecha=fecha_val,
                calificacion=cal,
            )
        )

        acumulado, conteo = por_asignacion.get(asignacion_id, (0.0, 0))
        por_asignacion[asignacion_id] = (acumulado + cal, conteo + 1)

    por_asignacion_list = [
        PromedioAsignacion(
            asignacion_id=int(asig_id),
            promedio=(total / count) if count else 0.0,
            evaluaciones=count,
        )
        for asig_id, (total, count) in sorted(por_asignacion.items())
    ]

    evaluaciones_registradas = len(serie)
    promedio_general = (
        sum(item.calificacion for item in serie) / evaluaciones_registradas
        if evaluaciones_registradas
        else None
    )

    mejor_nota = max((item.calificacion for item in serie), default=None)
    peor_nota = min((item.calificacion for item in serie), default=None)

    if evaluaciones_registradas >= 2:
        ultima = serie[-1].calificacion
        anterior = serie[-2].calificacion
        variacion = ultima - anterior
        en_mejora = variacion > 0
    elif evaluaciones_registradas == 1:
        ultima = serie[-1].calificacion
        anterior = None
        variacion = None
        en_mejora = None
    else:
        ultima = anterior = variacion = None
        en_mejora = None

    return ReporteEstudianteOut(
        estudiante_id=est_id,
        serie=serie,
        por_asignacion=por_asignacion_list,
        kpis=EstudianteKPIs(
            promedio_general=promedio_general,
            evaluaciones_registradas=evaluaciones_registradas,
            mejor_nota=mejor_nota,
            peor_nota=peor_nota,
        ),
        tendencia=TendenciaNotas(
            variacion=variacion,
            ultima=ultima,
            anterior=anterior,
            en_mejora=en_mejora,
        ),
    )


@router.get(
    "/curso/{asig_id}/promedios",
    response_model=ReporteCursoOut,
)
def promedios_curso(
    asig_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("REPORTES")),
):
    promedios_rows = (
        db.query(
            Nota.estudiante_id,
            func.avg(Nota.calificacion),
        )
        .join(Evaluacion, Nota.evaluacion_id == Evaluacion.id)
        .filter(Evaluacion.asignacion_id == asig_id)
        .group_by(Nota.estudiante_id)
        .order_by(Nota.estudiante_id.asc())
        .all()
    )

    promedios_por_estudiante = [
        PromedioEstudiante(
            estudiante_id=int(est_id),
            promedio=float(promedio),
        )
        for est_id, promedio in promedios_rows
    ]

    serie_evaluaciones_rows = (
        db.query(
            Evaluacion.id,
            Evaluacion.titulo,
            Evaluacion.fecha,
            func.avg(Nota.calificacion),
        )
        .outerjoin(Nota, Nota.evaluacion_id == Evaluacion.id)
        .filter(Evaluacion.asignacion_id == asig_id)
        .group_by(Evaluacion.id)
        .order_by(Evaluacion.fecha.asc(), Evaluacion.id.asc())
        .all()
    )

    serie_evaluaciones = [
        SerieEvaluacion(
            evaluacion_id=int(eval_id),
            titulo=str(titulo),
            fecha=_ensure_date(fecha),
            promedio=float(promedio) if promedio is not None else 0.0,
        )
        for eval_id, titulo, fecha, promedio in serie_evaluaciones_rows
    ]

    total_estudiantes = len(promedios_por_estudiante)
    promedio_general = (
        sum(item.promedio for item in promedios_por_estudiante) / total_estudiantes
        if total_estudiantes
        else None
    )

    aprobados = sum(1 for item in promedios_por_estudiante if item.promedio >= 51)
    tasa_aprobacion = (
        (aprobados / total_estudiantes) * 100 if total_estudiantes else 0.0
    )

    mejor_promedio = (
        max(promedios_por_estudiante, key=lambda item: item.promedio)
        if promedios_por_estudiante
        else None
    )
    peor_promedio = (
        min(promedios_por_estudiante, key=lambda item: item.promedio)
        if promedios_por_estudiante
        else None
    )

    if len(serie_evaluaciones) >= 2:
        variacion_eval = (
            serie_evaluaciones[-1].promedio - serie_evaluaciones[-2].promedio
        )
    else:
        variacion_eval = None

    return ReporteCursoOut(
        asignacion_id=asig_id,
        promedios_por_estudiante=promedios_por_estudiante,
        serie_evaluaciones=serie_evaluaciones,
        kpis=CursoKPIs(
            promedio_general=promedio_general,
            estudiantes=total_estudiantes,
            aprobados=aprobados,
            tasa_aprobacion=tasa_aprobacion,
            mejor_promedio=mejor_promedio,
            peor_promedio=peor_promedio,
            variacion_ultima_evaluacion=variacion_eval,
        ),
    )
