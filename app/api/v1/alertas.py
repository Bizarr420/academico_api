from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func, cast, Float
from datetime import date, timedelta

from app.api.deps import get_db
from app.api.deps_extra import require_view
from app.db.models import Alerta, Asistencia, Usuario
from app.schemas.alertas import AlertaOut, AlertaUpdate

router = APIRouter(tags=["alertas"])  # prefix lo pone router.py


def _get_asignacion_model():
    from app.db import models as m
    Asg = getattr(m, "AsignacionDocente", None)
    if Asg is None:
        raise HTTPException(500, "No se encontró modelo AsignacionDocente.")
    return Asg

def _get_models_for_promedio():
    from app.db import models as m
    Nota = getattr(m, "Nota", None)
    Evaluacion = getattr(m, "Evaluacion", None)
    if Nota is None or Evaluacion is None:
        raise HTTPException(500, "Faltan modelos Nota/Evaluacion.")
    col = getattr(Nota, "calificacion", None)
    if col is None:
        raise HTTPException(500, "Nota.calificacion no existe.")
    if not hasattr(Nota, "evaluacion_id"):
        raise HTTPException(500, "Nota.evaluacion_id no existe.")
    if not hasattr(Evaluacion, "asignacion_id"):
        raise HTTPException(500, "Evaluacion.asignacion_id no existe.")
    return Nota, Evaluacion, col

def _asistencia_bits(dias: int):
    # fecha DATE
    fecha_col = getattr(Asistencia, "fecha", None)
    if fecha_col is None:
        raise HTTPException(500, "Asistencia.fecha no existe.")
    # ausente por enum
    if not hasattr(Asistencia, "estado"):
        raise HTTPException(500, "Asistencia.estado no existe.")
    ausente_filter = Asistencia.estado.in_(["AUSENTE", "A"])  # ajustable si usas otros códigos
    # fk a asignación
    asig_col = getattr(Asistencia, "asignacion_id", None)
    if asig_col is None:
        raise HTTPException(500, "Asistencia.asignacion_id no existe.")
    # ventana (DATE con DATE)
    desde = date.today() - timedelta(days=dias)
    return fecha_col, desde, ausente_filter, asig_col


@router.get("/__test__")
def _test():
    return {"ok": True}


@router.post("/recalcular", status_code=status.HTTP_201_CREATED)
def recalcular_alertas(
    gestion: int = Query(..., ge=2000, le=2100),
    curso_id: int | None = Query(None),
    umbral_prom: int = Query(51, ge=0, le=100),
    faltas_max: int = Query(3, ge=0),
    dias: int = Query(30, ge=1),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("ALERTAS")),
):
    Asg = _get_asignacion_model()
    Nota, Evaluacion, nota_col = _get_models_for_promedio()

    # ---- 1) alcance: Asignaciones por gestion (tu modelo usa gestion_id) y opcional curso_id
    gestion_col = getattr(Asg, "gestion_id", None) or getattr(Asg, "gestion", None)
    if gestion_col is None:
        raise HTTPException(500, "AsignacionDocente no tiene gestion_id/gestion.")
    asg_stmt = select(Asg).where(gestion_col == gestion)
    if curso_id is not None:
        if not hasattr(Asg, "curso_id"):
            raise HTTPException(500, "AsignacionDocente no tiene curso_id.")
        asg_stmt = asg_stmt.where(Asg.curso_id == curso_id)
    asignaciones = db.execute(asg_stmt).scalars().all()
    if not asignaciones:
        return {"created": 0, "msg": "No hay asignaciones en ese alcance"}
    asg_ids = [a.id for a in asignaciones]

    # ---- 2) borrar alertas previas para el alcance
    del_ids = [x for (x,) in db.execute(
        select(Alerta.id).where(Alerta.gestion == gestion, Alerta.asignacion_id.in_(asg_ids))
    ).all()]
    if del_ids:
        db.query(Alerta).filter(Alerta.id.in_(del_ids)).delete(synchronize_session=False)
        db.commit()

    # ---- 3) promedios: Nota.calificacion -> join Evaluacion -> group (estudiante, asignacion)
    prom_stmt = (
        select(Nota.estudiante_id, Evaluacion.asignacion_id, func.avg(cast(nota_col, Float)))
        .join(Evaluacion, Evaluacion.id == Nota.evaluacion_id)
        .where(Evaluacion.asignacion_id.in_(asg_ids))
        .group_by(Nota.estudiante_id, Evaluacion.asignacion_id)
    )
    promedios = {(e, a): float(p) for e, a, p in db.execute(prom_stmt).all()}

    # ---- 4) inasistencias últimos X días (DATE vs DATE)
    fecha_col, desde, ausente_filter, asis_asig_col = _asistencia_bits(dias)
    falta_stmt = (
        select(Asistencia.estudiante_id, asis_asig_col, func.count())
        .where(asis_asig_col.in_(asg_ids), fecha_col >= desde, ausente_filter)
        .group_by(Asistencia.estudiante_id, asis_asig_col)
    )
    faltas = {(e, a): int(c) for e, a, c in db.execute(falta_stmt).all()}

    # ---- 5) generar alertas
    creadas = 0
    for a in asignaciones:
        universo = set(
            [e for (e, asgid) in promedios.keys() if asgid == a.id] +
            [e for (e, asgid) in faltas.keys() if asgid == a.id]
        )
        for est in universo:
            prom = promedios.get((est, a.id))
            fal = faltas.get((est, a.id), 0)

            if (prom is not None) and (prom < umbral_prom):
                db.add(Alerta(
                    gestion=gestion, asignacion_id=a.id, estudiante_id=est,
                    tipo="RIESGO_PROMEDIO",
                    motivo=f"promedio {int(prom)} < umbral {umbral_prom}",
                    score=max(0, min(100, 100 - (umbral_prom - int(prom)) * 2)),
                    estado="NUEVO",
                ))
                creadas += 1

            if fal > faltas_max:
                db.add(Alerta(
                    gestion=gestion, asignacion_id=a.id, estudiante_id=est,
                    tipo="RIESGO_ASISTENCIA",
                    motivo=f"inasistencias {fal} > {faltas_max} en {dias} días",
                    score=min(100, fal * 10),
                    estado="NUEVO",
                ))
                creadas += 1

    db.commit()
    return {"created": creadas}


# app/api/v1/alertas.py

@router.get("")
def listar(
    gestion: int | None = Query(None),
    curso_id: int | None = Query(None),
    estudiante_id: int | None = Query(None),
    estado: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("ALERTAS")),
):
    from app.db.models import Alerta, AsignacionDocente as Asg

    q = db.query(Alerta)
    if gestion is not None:
        q = q.filter(Alerta.gestion == gestion)
    if estudiante_id is not None:
        q = q.filter(Alerta.estudiante_id == estudiante_id)
    if estado:
        q = q.filter(Alerta.estado == estado)
    if curso_id is not None:
        q = q.join(Asg, Alerta.asignacion_id == Asg.id).filter(Asg.curso_id == curso_id)

    total = q.count()
    rows = (q.order_by(Alerta.id.desc())
              .offset((page - 1) * size)
              .limit(size)
              .all())

    items = [{
        "id": r.id,
        "gestion": r.gestion,
        "asignacion_id": r.asignacion_id,
        "estudiante_id": r.estudiante_id,
        "tipo": r.tipo,
        "motivo": r.motivo,
        "score": r.score,
        "estado": r.estado,
        "created_at": (r.created_at.isoformat() if getattr(r, "created_at", None) else None),
    } for r in rows]

    return {"items": items, "total": total, "page": page, "size": size}


@router.put("/{alerta_id}", response_model=AlertaOut)
def actualizar(
    alerta_id: int,
    payload: AlertaUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("ALERTAS")),
):
    obj = db.get(Alerta, alerta_id)
    if not obj:
        raise HTTPException(404, "Alerta no encontrada")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)

    db.commit()
    db.refresh(obj)
    # 🔧 clave: validar con from_attributes=True para Pydantic v2
    return AlertaOut.model_validate(obj, from_attributes=True)
