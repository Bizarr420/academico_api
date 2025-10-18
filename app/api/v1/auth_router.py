from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.deps_extra import get_auth_context
from app.core.security import create_access_token
from app.schemas.auth import Token
from app.schemas.usuarios import SessionInfo
from .auth import authenticate_user
from app.db.models import Usuario

router = APIRouter()

@router.post("/login", response_model=Token)
def login_for_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token({
        "sub": user.username,
        "user_id": user.id,
        "username": user.username
    })
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=SessionInfo)
def read_users_me(context = Depends(get_auth_context)):
    return SessionInfo(
        user=context.user,
        rol_codigo=getattr(context, "rol_codigo", None),
        permisos=sorted(getattr(context, "permissions", [])),
    )

# Endpoint de logout que elimina la cookie JWT
from fastapi import Response

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"detail": "Logout successful"}
