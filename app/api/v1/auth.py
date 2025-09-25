from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.api.deps import get_db
from app.core.security import verify_password, create_access_token, hash_password
from app.schemas.usuarios import Token, UsuarioCreate
from app.db.models import Usuario, Persona, EstadoUsuarioEnum
import traceback
import sys

router = APIRouter()

@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    u = db.query(Usuario).filter(Usuario.username == form.username).first()
    if not u or not verify_password(form.password, u.password_hash):
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")
    return Token(access_token=create_access_token(subject=u.username))

@router.post("/register", response_model=dict)
def register(data: UsuarioCreate, db: Session = Depends(get_db)):
    try:
        # username único
        if db.query(Usuario).filter(Usuario.username == data.username).first():
            raise HTTPException(status_code=400, detail="Usuario ya existe")
        # SQLAlchemy 2.0
        persona = db.get(Persona, data.persona_id)
        if not persona:
            raise HTTPException(status_code=404, detail="Persona no encontrada")

        u = Usuario(
            persona_id=data.persona_id,
            username=data.username,
            password_hash=hash_password(data.password),
            rol_id=data.rol_id,
            estado=EstadoUsuarioEnum.ACTIVO
        )
        db.add(u); db.commit(); db.refresh(u)
        return {"id": u.id, "username": u.username}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print("Error creando evaluación:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"error interno")
from fastapi import Depends
from app.api.deps import get_current_user
from app.db.models import Usuario
from pydantic import BaseModel, Field
from app.core.security import verify_password, hash_password

class PasswordChangeIn(BaseModel):
    old_password: str = Field(min_length=6)
    new_password: str = Field(min_length=6)

@router.get("/me")
def me(current_user: Usuario = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "persona_id": current_user.persona_id,
        "rol_id": current_user.rol_id,
        "estado": current_user.estado,
    }

@router.post("/change-password")
def change_password(data: PasswordChangeIn, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    if not verify_password(data.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")
    current_user.password_hash = hash_password(data.new_password)
    db.add(current_user); db.commit()
    return {"detail": "Contraseña actualizada"}
