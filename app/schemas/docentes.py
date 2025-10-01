from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.personas import PersonaCreate, PersonaOut


class DocenteBase(BaseModel):
    titulo: str | None = Field(default=None, max_length=120)
    profesion: str | None = Field(default=None, max_length=120)


class DocenteCreate(DocenteBase):
    persona_id: int | None = Field(default=None, gt=0)
    persona: PersonaCreate | None = None

    @model_validator(mode="after")
    def check_persona_reference(self) -> "DocenteCreate":
        persona_id_provided = self.persona_id is not None
        persona_object_provided = self.persona is not None
        if persona_id_provided == persona_object_provided:
            raise ValueError("Debe proporcionar únicamente persona_id o persona")
        return self


class DocenteUpdate(BaseModel):
    titulo: str | None = Field(default=None, max_length=120)
    profesion: str | None = Field(default=None, max_length=120)


class DocenteOut(DocenteBase):
    id: int
    persona_id: int
    persona: PersonaOut | None = None

    model_config = ConfigDict(from_attributes=True)
