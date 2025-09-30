# app/api/v1/materias.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
#from app.api.deps_extra import require_role
from app.api.deps_extra import require_view
from app.db.models import Materia, Usuario
from app.schemas.materias import MateriaCreate, MateriaOut, MateriaUpdate
from sqlalchemy.exc import IntegrityError
from fastapi import status

router = APIRouter(
    prefix="/materias",
    tags=["materias"],
    #dependencies=[Depends(require_role("ADMIN", "DOCENTE"))]
)


@router.get("", response_model=list[MateriaOut])
def listar_materias(
    q: str | None = Query(None),
    area: str | None = Query(None),
    estado: str | None = Query(None),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("MATERIAS")),
):
    query = db.query(Materia)
    if q:
        q_like = f"%{q}%"
        query = query.filter((Materia.nombre.ilike(q_like)) | (Materia.codigo.ilike(q_like)))
    if area:
        query = query.filter(Materia.area.ilike(f"%{area}%"))
    if estado:
        estado_norm = estado.strip().upper()
        if estado_norm not in {"ACTIVO", "INACTIVO"}:
            raise HTTPException(status_code=400, detail="estado inválido")
        query = query.filter(Materia.estado == estado_norm)
    return query.order_by(Materia.nombre.asc()).all()

@router.post("", response_model=MateriaOut, status_code=status.HTTP_201_CREATED)
def crear_materia(
    data: MateriaCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("MATERIAS")),
):
    try:
        # opcional: check rápido por código duplicado
        if db.query(Materia).filter(Materia.codigo == data.codigo).first():
            raise HTTPException(status_code=400, detail="codigo ya existe")

        payload = data.model_dump()
        payload["estado"] = payload["estado"].upper()
        if payload["estado"] not in {"ACTIVO", "INACTIVO"}:
            raise HTTPException(status_code=400, detail="estado inválido")
        m = Materia(**payload)
        db.add(m)
        db.commit()
        db.refresh(m)
        return m

    except IntegrityError as e:
        db.rollback()
        # si igualmente se coló una violación única u otra constraint
        raise HTTPException(status_code=400, detail="violación de integridad (¿código duplicado o columna obligatoria?)")

    except Exception as e:
        db.rollback()
        # 👇 para depurar rápido mientras desarrollas:
        raise HTTPException(status_code=400, detail=f"error al crear materia: {str(e)}")

@router.put("/{materia_id}", response_model=MateriaOut)
def editar_materia(
    materia_id:int,
    data: MateriaUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("MATERIAS")),
):
    m = db.get(Materia, materia_id)
    if not m:
        raise HTTPException(404, "Materia no encontrada")
    if data.codigo and data.codigo != m.codigo:
        if db.query(Materia).filter(Materia.codigo == data.codigo).first():
            raise HTTPException(400, "codigo ya existe")
    for k, v in data.model_dump(exclude_unset=True).items():
        if k == "estado" and v is not None:
            estado_norm = v.upper()
            if estado_norm not in {"ACTIVO", "INACTIVO"}:
                raise HTTPException(status_code=400, detail="estado inválido")
            setattr(m, k, estado_norm)
        else:
            setattr(m, k, v)
    db.commit(); db.refresh(m)
    return m

@router.delete("/{materia_id}")
def borrar_materia(
    materia_id:int,
    db:Session=Depends(get_db),
    _: Usuario = Depends(require_view("MATERIAS")),
):
    m = db.get(Materia, materia_id)
    if not m: raise HTTPException(404, "Materia no encontrada")
    db.delete(m); db.commit()
    return {"ok": True}

@router.post("/__echo__")
def echo(data: MateriaCreate):
    return data

