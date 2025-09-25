from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, get_db
from app.core.security import verify_password, create_access_token, hash_password
from app.schemas.usuarios import LoginResponse, UsuarioCreate, UsuarioOut
from app.db.models import Usuario, Persona, EstadoUsuarioEnum
from pydantic import BaseModel, Field, ValidationError
import traceback
import sys

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login", response_model=LoginResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    content_type = request.headers.get("content-type", "")

    if content_type.startswith("application/json"):
        try:
            payload = await request.json()
        except Exception as exc:  # pragma: no cover - body parsing guard
            raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos") from exc
        try:
            credentials = LoginRequest.model_validate(payload)
        except ValidationError as exc:
            raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos") from exc
    else:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        if not username or not password:
            raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")
        credentials = LoginRequest(username=username, password=password)

    u = db.query(Usuario).filter(Usuario.username == credentials.username).first()
    if not u or not verify_password(credentials.password, u.password_hash):
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")
    token = create_access_token(subject=u.username)
    user_payload = UsuarioOut.model_validate(u, from_attributes=True)
    return LoginResponse(access_token=token, user=user_payload)

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

class PasswordChangeIn(BaseModel):
    old_password: str = Field(min_length=6)
    new_password: str = Field(min_length=6)

@router.get("/me", response_model=UsuarioOut)
def me(current_user: Usuario = Depends(get_current_user)):
    return UsuarioOut.model_validate(current_user, from_attributes=True)

@router.post("/change-password")
def change_password(data: PasswordChangeIn, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    if not verify_password(data.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")
    current_user.password_hash = hash_password(data.new_password)
    db.add(current_user); db.commit()
    return {"detail": "Contraseña actualizada"}
