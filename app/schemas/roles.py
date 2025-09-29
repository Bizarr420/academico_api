from pydantic import BaseModel, Field


class VistaOut(BaseModel):
    id: int
    nombre: str
    codigo: str

    class Config:
        from_attributes = True


class RolBase(BaseModel):
    nombre: str = Field(min_length=1, max_length=30)
    codigo: str = Field(min_length=1, max_length=20)


class RolCreate(RolBase):
    vista_ids: list[int] = Field(default_factory=list)


class RolUpdate(RolBase):
    vista_ids: list[int] | None = None


class RolOut(RolBase):
    id: int
    vistas: list[VistaOut] = Field(default_factory=list)

    class Config:
        from_attributes = True
