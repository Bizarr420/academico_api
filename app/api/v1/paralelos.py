from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.db.models import Paralelo

router = APIRouter()

@router.get("/")
def listar_paralelos(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Paralelo).order_by(Paralelo.id.asc()).all()

@router.post("/")
def crear_paralelo(data: dict, db: Session = Depends(get_db), _=Depends(get_current_user)):
    p = Paralelo(**data)
    db.add(p); db.commit(); db.refresh(p)
    return p
