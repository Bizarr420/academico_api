from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.api.deps_extra import require_view
from app.db.models import Paralelo, Usuario

router = APIRouter()

@router.get("/")
def listar_paralelos(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("PARALELOS")),
):
    return db.query(Paralelo).order_by(Paralelo.id.asc()).all()

@router.post("/")
def crear_paralelo(
    data: dict,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("PARALELOS")),
):
    p = Paralelo(**data)
    db.add(p); db.commit(); db.refresh(p)
    return p
