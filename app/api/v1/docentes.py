def get_docente_with_relations(docente, db):
    from app.db.models import AsignacionDocente, Materia, Curso, Paralelo
    from app.schemas.docentes import AsignacionDocenteOut, ParaleloOut
    from app.schemas.materias import MateriaOut
    from app.schemas.cursos import CursoOut

    asignaciones = db.query(AsignacionDocente).filter(AsignacionDocente.docente_id == docente.id).all()
    materia_ids = list({a.materia_id for a in asignaciones})
    curso_ids = list({a.curso_id for a in asignaciones})
    materias = db.query(Materia).filter(Materia.id.in_(materia_ids)).all() if materia_ids else []
    cursos = db.query(Curso).filter(Curso.id.in_(curso_ids)).all() if curso_ids else []
    docente.materias = materias
    docente.cursos = cursos

    asignaciones_out = []
    for asignacion in asignaciones:
        materia = next((m for m in materias if m.id == asignacion.materia_id), None)
        curso = next((c for c in cursos if c.id == asignacion.curso_id), None)
        paralelo = db.query(Paralelo).filter(Paralelo.id == asignacion.paralelo_id).first()
        if materia and curso and paralelo:
            asignaciones_out.append(
                AsignacionDocenteOut(
                    id=asignacion.id,
                    gestion_id=asignacion.gestion_id,
                    materia=MateriaOut.model_validate(materia),
                    curso=CursoOut.model_validate(curso),
                    paralelo=ParaleloOut.model_validate(paralelo)
                )
            )
    docente.asignaciones = asignaciones_out
    return docente
from typing import List, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.deps_extra import require_role_and_view, require_view
from app.db.models import Docente, Persona, Usuario
from app.schemas.docentes import DocenteCreate, DocenteOut, DocenteUpdate
from app.services.personas import create_persona

router = APIRouter(tags=["docentes"])


@router.get("/", response_model=List[DocenteOut])
def listar_docentes(
    db: Session = Depends(get_db),
    persona_id: int | None = Query(None, ge=1),
    estado: Literal["ACTIVO", "INACTIVO", "TODOS"] = Query("ACTIVO"),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    _: Usuario = Depends(require_view("DOCENTES")),
):
    from app.db.models import AsignacionDocente, Materia, Curso

    q = db.query(Docente)
    if persona_id is not None:
        q = q.filter(Docente.persona_id == persona_id)
    if estado != "TODOS":
        q = q.filter(Docente.estado == estado)
    docentes = q.order_by(Docente.id).offset(offset).limit(limit).all()
    result = [get_docente_with_relations(docente, db) for docente in docentes]
    return result


@router.get("/{docente_id}", response_model=DocenteOut)
def obtener_docente(
    docente_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("DOCENTES")),
):
    docente = db.get(Docente, docente_id)
    if not docente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Docente no encontrado")
    return docente


@router.post(
    "/",
    response_model=DocenteOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_docente(
    payload: DocenteCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_role_and_view({"admin"}, "DOCENTES")),
):
    if payload.persona is not None:
        try:
            persona = create_persona(db, payload.persona)
            existe = db.query(Docente).filter(Docente.persona_id == persona.id).first()
            if existe:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Docente ya existe para la persona",
                )


            docente = Docente(
                persona_id=persona.id,
                titulo=payload.titulo,
                profesion=payload.profesion,
                estado=payload.estado,
            )
            db.add(docente)
            db.commit()
            db.refresh(docente)

            # Asignar materia y cursos si se reciben
            if payload.materia_id:
                from app.db.models import AsignacionDocente, Paralelo
                gestion_id = db.execute("SELECT id FROM gestion ORDER BY id DESC LIMIT 1").scalar()  # Ajusta según tu lógica de gestión
                if payload.curso_ids:
                    for curso_id in payload.curso_ids:
                        paralelo = db.query(Paralelo).filter(Paralelo.curso_id == curso_id).first()
                        if not paralelo:
                            continue  # O puedes lanzar un error si es obligatorio
                        asignacion = AsignacionDocente(
                            gestion_id=gestion_id,
                            docente_id=docente.id,
                            materia_id=payload.materia_id,
                            curso_id=curso_id,
                            paralelo_id=paralelo.id
                        )
                        db.add(asignacion)
                db.commit()

        except Exception:
            db.rollback()
            raise

    db.refresh(docente)
    db.refresh(docente, attribute_names=["persona"])
    return get_docente_with_relations(docente, db)

    persona = db.get(Persona, payload.persona_id)
    if not persona:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Persona no encontrada")

    existe = db.query(Docente).filter(Docente.persona_id == payload.persona_id).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Docente ya existe para la persona",
        )

    docente = Docente(
        persona_id=payload.persona_id,
        titulo=payload.titulo,
        profesion=payload.profesion,
        estado=payload.estado,
    )
    db.add(docente)
    db.commit()

    # Asignar materia y cursos si se reciben
    if payload.materia_id:
        from app.db.models import AsignacionDocente, Paralelo
        gestion_id = db.execute("SELECT id FROM gestion ORDER BY id DESC LIMIT 1").scalar()  # Ajusta según tu lógica de gestión
        if payload.curso_ids:
            for curso_id in payload.curso_ids:
                paralelo = db.query(Paralelo).filter(Paralelo.curso_id == curso_id).first()
                if not paralelo:
                    continue  # O puedes lanzar un error si es obligatorio
                asignacion = AsignacionDocente(
                    gestion_id=gestion_id,
                    docente_id=docente.id,
                    materia_id=payload.materia_id,
                    curso_id=curso_id,
                    paralelo_id=paralelo.id
                )
                db.add(asignacion)
        else:
            # Si no hay cursos, no se puede asignar paralelo
            pass
        db.commit()

    db.refresh(docente)
    db.refresh(docente, attribute_names=["persona"])
    return get_docente_with_relations(docente, db)


@router.patch(
    "/{docente_id}",
    response_model=DocenteOut,
)
def actualizar_docente(
    docente_id: int,
    payload: DocenteUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_role_and_view({"admin"}, "DOCENTES")),
):
    docente = db.get(Docente, docente_id)
    if not docente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Docente no encontrado")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(docente, key, value)

    db.add(docente)
    db.commit()
    db.refresh(docente)
    return docente
