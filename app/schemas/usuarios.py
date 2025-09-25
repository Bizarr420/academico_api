from pydantic import BaseModel, Field

class UsuarioCreate(BaseModel):
    persona_id: int
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6)
    rol_id: int | None = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
