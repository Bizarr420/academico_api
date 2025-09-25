# app/api/roles.py
from fastapi import Depends, HTTPException, status
from app.api.deps import get_current_user

def role_required(*roles):
    def _dep(user=Depends(get_current_user)):
        if user.rol_id not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permisos insuficientes")
        return user
    return _dep
