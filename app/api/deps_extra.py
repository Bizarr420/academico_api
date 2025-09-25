from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.db.models import Rol  # ajusta si tu modelo se llama distinto

def require_role(*codes):
    # Permite: require_role("ADMIN","DOC")  o  require_role({"ADMIN","DOC"})
    if len(codes) == 1 and isinstance(codes[0], (set, list, tuple)):
        allowed = {str(c).upper() for c in codes[0]}
    else:
        allowed = {str(c).upper() for c in codes}

    def _dep(user=Depends(get_current_user), db: Session = Depends(get_db)):
        rol = db.get(Rol, getattr(user, "rol_id", None)) if getattr(user, "rol_id", None) else None
        if not rol or str(rol.codigo).upper() not in allowed:
            raise HTTPException(status_code=403, detail="Permisos insuficientes")
    return _dep
