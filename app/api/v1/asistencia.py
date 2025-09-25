# app/api/v1/asistencias.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import date
from app.api.deps import get_db, get_current_user
from app.api.deps_extra import require_role
from app.db.models import Asistencia, Matricula
from app.schemas.asistencias import AsistenciaCreate, AsistenciaOut, AsistenciaMasivaIn

router = APIRouter(tags=["asistencias"])

@router.post("/", response_model=AsistenciaOut, dependencies=[Depends(require_role("ADMIN", "DOC"))])
def crear_asistencia(data: AsistenciaCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    ok_mat = db.execute(
        select(Matricula.id).where(
            Matricula.asignacion_id == data.asignacion_id,
            Matricula.estudiante_id == data.estudiante_id,
        )
    ).scalar_one_or_none()
    if not ok_mat:
        raise HTTPException(status_code=400, detail="El estudiante no está matriculado en esta asignación")

    existente = (db.query(Asistencia)
                   .filter_by(fecha=data.fecha, asignacion_id=data.asignacion_id, estudiante_id=data.estudiante_id)
                   .first())
    if existente:
        existente.estado = data.estado
        if hasattr(data, "observacion"):
            existente.observacion = data.observacion
        db.commit(); db.refresh(existente)
        return existente

    obj = Asistencia(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.post("/masivo", dependencies=[Depends(require_role("DOC","ADMIN"))])
def crear_asistencia_masiva(payload: AsistenciaMasivaIn, db: Session = Depends(get_db), _=Depends(get_current_user)):
    inserciones = duplicados = no_matric = 0
    for item in payload.items:
        ok_mat = db.execute(
            select(Matricula.id).where(
                Matricula.asignacion_id == payload.asignacion_id,
                Matricula.estudiante_id == item.estudiante_id
            )
        ).scalar_one_or_none()
        if not ok_mat:
            no_matric += 1
            continue

        ya = db.execute(
            select(Asistencia.id).where(
                Asistencia.fecha == payload.fecha,
                Asistencia.asignacion_id == payload.asignacion_id,
                Asistencia.estudiante_id == item.estudiante_id
            )
        ).scalar_one_or_none()
        if ya:
            duplicados += 1
            continue

        db.add(Asistencia(
            fecha=payload.fecha,
            asignacion_id=payload.asignacion_id,
            estudiante_id=item.estudiante_id,
            estado=item.estado,
            observacion=getattr(item, "observacion", None),
        ))
        inserciones += 1

    db.commit()
    return {"insertados": inserciones, "duplicados": duplicados, "no_matriculados": no_matric}

@router.get("/", response_model=list[AsistenciaOut], dependencies=[Depends(require_role("ADMIN","DOC"))])
def listar_asistencias(
    asignacion_id: int = Query(..., gt=0),
    fecha: date | None = None,
    desde: date | None = None,
    hasta: date | None = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    q = db.query(Asistencia).where(Asistencia.asignacion_id == asignacion_id)
    if fecha:
        q = q.where(Asistencia.fecha == fecha)
    if desde:
        q = q.where(Asistencia.fecha >= desde)
    if hasta:
        q = q.where(Asistencia.fecha <= hasta)
    return q.order_by(Asistencia.fecha.asc(), Asistencia.estudiante_id.asc()).all()

@router.get("/estudiante/{est_id}", response_model=list[AsistenciaOut], dependencies=[Depends(require_role("ADMIN","DOC","PAD"))])
def asistencias_estudiante(est_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Asistencia).where(Asistencia.estudiante_id == est_id).order_by(Asistencia.fecha.desc()).all()
