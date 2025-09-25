from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.security import decode_token
from app.db.models import Usuario, EstadoUsuarioEnum

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    creds = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = decode_token(token)
        username = payload.get("sub")
        if not username: raise creds
    except Exception:
        raise creds
    user = db.query(Usuario).filter(Usuario.username == username).first()
    if not user or user.estado != EstadoUsuarioEnum.ACTIVO: raise creds
    return user
from fastapi import Depends, HTTPException
from app.db.models import Usuario

def require_roles(*roles_validos: str):
    def dep(current_user: Usuario = Depends(get_current_user)):
        if current_user.rol and current_user.rol.nombre in roles_validos:
            return current_user
        raise HTTPException(status_code=403, detail="Permisos insuficientes")
    return dep

def require_role(*roles):
    def wrapper(user: Usuario = Depends(get_current_user)):
        if not user.rol_id or user.rol_id not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permisos insuficientes")
        return user
    return wrapper