from pydantic import BaseModel, Field

from app.db.models import EstadoUsuarioEnum
from app.schemas.personas import PersonaOut
from app.schemas.roles import RolOut

class UsuarioCreate(BaseModel):
    persona_id: int
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6)
    rol_id: int = Field(gt=0)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UsuarioUpdate(BaseModel):
    rol_id: int = Field(gt=0)
    estado: EstadoUsuarioEnum | None = None


class UsuarioOut(BaseModel):
    id: int
    username: str
    persona_id: int
    rol_id: int | None = None
    estado: EstadoUsuarioEnum
    persona: PersonaOut | None = None
    rol: RolOut | None = None

    class Config:
        from_attributes = True


class LoginResponse(Token):
    user: UsuarioOut
