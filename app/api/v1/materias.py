# app/api/v1/materias.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
#from app.api.deps_extra import require_role
from app.db.models import Materia
from app.schemas.materias import MateriaCreate, MateriaOut, MateriaUpdate
from sqlalchemy.exc import IntegrityError
from fastapi import status

router = APIRouter(
    prefix="/materias",
    tags=["materias"],
    #dependencies=[Depends(require_role("ADMIN", "DOCENTE"))]
)


@router.get("", response_model=list[MateriaOut])
def listar_materias(q: str | None = Query(None), db: Session = Depends(get_db), _=Depends(get_current_user)):
    query = db.query(Materia)
    if q:
        q_like = f"%{q}%"
        query = query.filter((Materia.nombre.ilike(q_like)) | (Materia.codigo.ilike(q_like)))
    return query.order_by(Materia.nombre.asc()).all()

@router.post("", response_model=MateriaOut, status_code=status.HTTP_201_CREATED)
def crear_materia(data: MateriaCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    try:
        # opcional: check rápido por código duplicado
        if db.query(Materia).filter(Materia.codigo == data.codigo).first():
            raise HTTPException(status_code=400, detail="codigo ya existe")

        m = Materia(**data.model_dump())
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
def editar_materia(materia_id:int, data: MateriaUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    m = db.get(Materia, materia_id)
    if not m:
        raise HTTPException(404, "Materia no encontrada")
    if data.codigo and data.codigo != m.codigo:
        if db.query(Materia).filter(Materia.codigo == data.codigo).first():
            raise HTTPException(400, "codigo ya existe")
    for k,v in data.model_dump(exclude_unset=True).items():
        setattr(m, k, v)
    db.commit(); db.refresh(m)
    return m

@router.delete("/{materia_id}")
def borrar_materia(materia_id:int, db:Session=Depends(get_db), _=Depends(get_current_user)):
    m = db.get(Materia, materia_id)
    if not m: raise HTTPException(404, "Materia no encontrada")
    db.delete(m); db.commit()
    return {"ok": True}

@router.post("/__echo__")
def echo(data: MateriaCreate):
    return data

