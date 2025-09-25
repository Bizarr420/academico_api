from pydantic import BaseModel, Field


class DocenteBase(BaseModel):
    persona_id: int = Field(gt=0)
    titulo: str | None = Field(default=None, max_length=120)


class DocenteCreate(DocenteBase):
    pass


class DocenteOut(DocenteBase):
    id: int

    class Config:
        from_attributes = True
