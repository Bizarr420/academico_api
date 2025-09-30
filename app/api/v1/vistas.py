from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.deps_extra import require_view
from app.db.models import Usuario, Vista
from app.schemas.roles import VistaOut

router = APIRouter(tags=["vistas"])


@router.get("/", response_model=List[VistaOut])
def listar_vistas(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_view("VISTAS")),
):
    return db.query(Vista).order_by(Vista.nombre).all()
