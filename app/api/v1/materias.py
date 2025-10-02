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
    incluir_inactivos: bool = Query(False, alias="incluir_inactivos"),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("MATERIAS")),
):
    query = db.query(Materia)

    if not estado and not incluir_inactivos:
        query = query.filter(Materia.estado == "ACTIVO")

    if q:
        q_like = f"%{q}%"
        query = query.filter((Materia.nombre.ilike(q_like)) | (Materia.codigo.ilike(q_like)))
    if area:
        query = query.filter(Materia.area.ilike(f"%{area}%"))

    if estado:
        estado_norm = estado.strip().upper()
        if estado_norm not in {"ACTIVO", "INACTIVO", "TODOS"}:
            raise HTTPException(status_code=400, detail="estado inválido")
        if estado_norm != "TODOS":
            query = query.filter(Materia.estado == estado_norm)

    return query.order_by(Materia.nombre.asc()).all()

@router.post("", response_model=MateriaOut, status_code=status.HTTP_201_CREATED)
def crear_materia(
    data: MateriaCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("MATERIAS")),
):
    try:
        existing_codigo = (
            db.query(Materia).filter(Materia.codigo == data.codigo).first()
        )
        if existing_codigo:
            detail = {
                "error": "codigo_en_uso",
                "mensaje": "Código de materia ya registrado.",
                "materia_id": existing_codigo.id,
                "estado": existing_codigo.estado,
            }
            raise HTTPException(status_code=409, detail=detail)

        existing_nombre = (
            db.query(Materia).filter(Materia.nombre == data.nombre).first()
        )
        if existing_nombre:
            detail = {
                "error": "nombre_en_uso",
                "mensaje": "Nombre de materia ya registrado.",
                "materia_id": existing_nombre.id,
                "estado": existing_nombre.estado,
            }
            raise HTTPException(status_code=409, detail=detail)

        payload = data.model_dump()
        estado_payload = payload.get("estado", "ACTIVO")
        estado_norm = estado_payload.upper() if estado_payload else "ACTIVO"
        if estado_norm not in {"ACTIVO", "INACTIVO"}:
            raise HTTPException(status_code=400, detail="estado inválido")
        payload["estado"] = estado_norm

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
        existing_codigo = (
            db.query(Materia)
            .filter(Materia.codigo == data.codigo, Materia.id != m.id)
            .first()
        )
        if existing_codigo:
            detail = {
                "error": "codigo_en_uso",
                "mensaje": "Código de materia ya registrado.",
                "materia_id": existing_codigo.id,
                "estado": existing_codigo.estado,
            }
            raise HTTPException(status_code=409, detail=detail)

    if data.nombre and data.nombre != m.nombre:
        existing_nombre = (
            db.query(Materia)
            .filter(Materia.nombre == data.nombre, Materia.id != m.id)
            .first()
        )
        if existing_nombre:
            detail = {
                "error": "nombre_en_uso",
                "mensaje": "Nombre de materia ya registrado.",
                "materia_id": existing_nombre.id,
                "estado": existing_nombre.estado,
            }
            raise HTTPException(status_code=409, detail=detail)
    for k, v in data.model_dump(exclude_unset=True).items():
        if k == "estado" and v is not None:
            estado_norm = v.upper()
            if estado_norm not in {"ACTIVO", "INACTIVO"}:
                raise HTTPException(status_code=400, detail="estado inválido")
            setattr(m, k, estado_norm)
        else:
            setattr(m, k, v)
    db.commit()
    db.refresh(m)
    return m

@router.delete("/{materia_id}")
def borrar_materia(
    materia_id:int,
    db:Session=Depends(get_db),
    _: Usuario = Depends(require_view("MATERIAS")),
):
    m = db.get(Materia, materia_id)
    if not m:
        raise HTTPException(404, "Materia no encontrada")

    if m.estado == "INACTIVO":
        return {"ok": True, "mensaje": "Materia ya estaba inactiva"}

    m.estado = "INACTIVO"
    db.commit()
    db.refresh(m)
    return {"ok": True}


@router.post("/{materia_id}/restore", response_model=MateriaOut)
def restaurar_materia(
    materia_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("MATERIAS")),
):
    materia = db.get(Materia, materia_id)
    if not materia:
        raise HTTPException(404, "Materia no encontrada")

    materia.estado = "ACTIVO"
    db.commit()
    db.refresh(materia)
    return materia

@router.post("/__echo__")
def echo(data: MateriaCreate):
    return data

