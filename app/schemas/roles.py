from pydantic import BaseModel, Field


class RolBase(BaseModel):
    nombre: str = Field(min_length=1, max_length=30)
    codigo: str = Field(min_length=1, max_length=20)


class RolCreate(RolBase):
    pass


class RolOut(RolBase):
    id: int

    class Config:
        from_attributes = True
